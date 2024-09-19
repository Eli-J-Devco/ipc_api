import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.schema import CreateTable
from sqlalchemy import MetaData, Table, Column, select, text, ForeignKey, func, update

from .create_table_model import CreateTableModel

from ..async_db.src.async_db.wrapper import async_db_request_handler
from ..devices_entity import (Devices as DevicesEntity,
                              PointList as PointListEntity,
                              DeviceMppt as DeviceMpptEntity,
                              DeviceMpptString as DeviceMpptStringEntity,
                              DevicePanel as DevicePanelEntity,
                              DevicePointListMap as DevicePointListMapEntity,
                              DeviceConnection as DeviceConnectionEntity, )
from ..devices_model import (Point,
                             DeviceModel,
                             PointType,
                             DeviceMppt,
                             DeviceMpptString,
                             DevicePanel,
                             DevicePointListMap,
                             DeviceConnection)

logger = logging.getLogger(__name__)


class TableColumn:
    def __init__(self, column_name: str, column_type):
        self.column_name = column_name
        self.column_type = column_type


class CreateTableRepository:
    @staticmethod
    def create_table(table_name: str, table_schema: List[TableColumn], meta: MetaData):
        try:
            logging.info(f"Creating table {table_name}")
            is_table = meta.tables.__dict__.get(table_name)
            if is_table:
                logging.info(f"Table {table_name} already exists")
                raise Exception(f"Table {table_name} already exists")

            default_columns_config = CreateTableModel.default
            default_columns = [Column(name=default_columns_config[col].name,
                                      type_=default_columns_config[col].col_type,
                                      nullable=default_columns_config[col].nullable,
                                      primary_key=default_columns_config[col].primary_key,
                                      *[ForeignKey(default_columns_config[col].foreign_key["name"],
                                                   ondelete=default_columns_config[col].foreign_key["ondelete"],
                                                   onupdate=default_columns_config[col].foreign_key["onupdate"])]
                                      if default_columns_config[col].foreign_key else []
                                      ) for col in default_columns_config]
            new_table = Table(table_name,
                              meta,
                              *default_columns,
                              extend_existing=True)

            for column in table_schema:
                new_table.append_column(Column(column.column_name, column.column_type), replace_existing=True)

            new_table = CreateTable(new_table, if_not_exists=True)
            del default_columns
            return new_table
        except Exception as e:
            logging.error(f"Error when creating {table_name}: {e}")
            raise e


class CreateTableService:
    def __init__(self,
                 metadata: MetaData,
                 table_repository: CreateTableRepository = CreateTableRepository()):
        self.table_repository = table_repository
        self.metadata = metadata

    @async_db_request_handler
    async def create_table(self, table_name: str, table_schema: List[TableColumn], session: AsyncSession):
        query = str(self.table_repository.create_table(table_name, table_schema, self.metadata)).replace('"', '')
        await session.execute(text(query))
        logging.info(f"Table {table_name} created")

    @async_db_request_handler
    async def validate_table(self, device_id: int, table_name: str, session: AsyncSession):
        query = f"SELECT * FROM {table_name} WHERE id_device_list = {device_id}"
        result = await session.execute(text(query))

        if result.scalars().all() == 0:
            logging.info(f"Table {table_name} not found")
            return False

        return True

    @async_db_request_handler
    async def get_need_mapping_connection(self, device_id: int, session: AsyncSession) -> list[int]:
        query = (select(DevicesEntity)
                 .join(DeviceConnectionEntity, DevicesEntity.id == DeviceConnectionEntity.device_list_id)
                 .filter(DevicesEntity.parent == device_id))
        result = await session.execute(query)
        devices = result.scalars().all()

        return [device.id for device in devices]

    @async_db_request_handler
    async def add_connection(self, connection: DeviceConnection, session: AsyncSession):
        new_connection = DeviceConnectionEntity(**connection.dict())
        session.add(new_connection)
        await session.flush()

    @async_db_request_handler
    async def update_device_connection(self, device_id: int, connection_id: int, session: AsyncSession):
        query = (update(DeviceConnectionEntity)
                 .where(DeviceConnectionEntity.device_list_id == device_id)
                 .values(connect_device_id=connection_id))
        await session.execute(query)

    @async_db_request_handler
    async def add_device_mppt(self, device: DeviceModel, session: AsyncSession):
        logging.info(f"Adding device mppt for {device.table_name}")
        query = (select(PointListEntity)
                 .where(PointListEntity.id_template == device.id_template)
                 .where(PointListEntity.id_config_information == PointType.MPPT.value))
        result = await session.execute(query)
        points = result.scalars().all()

        if not points:
            logging.error(f"No mppt points found for {device.table_name}")
            await self.add_device_string(device, None, None, session=session)
            return

        need_mapping_connection = await self.get_need_mapping_connection(device.id, session=session)
        for point in points:
            new_device_mppt = DeviceMpptEntity(**DeviceMppt(**point.__dict__,
                                                            id_point_list=point.id,
                                                            namekey=point.id_pointkey,
                                                            id_device_list=device.id).dict(exclude={"id"}))
            session.add(new_device_mppt)
            await session.flush()

            if need_mapping_connection:
                await self.update_device_connection(need_mapping_connection.pop(0), new_device_mppt.id, session=session)

            await self.add_device_string(device, point.id, new_device_mppt.id, session=session)
        logging.info(f"Device mppt of {device.table_name} added")

    @async_db_request_handler
    async def add_device_string(self,
                                device: DeviceModel,
                                point_id: int,
                                id_device_mppt: int,
                                session: AsyncSession):
        logging.info(f"Adding device string for {device.table_name}")
        query = (select(PointListEntity)
                 .where(PointListEntity.id_template == device.id_template)
                 .where(PointListEntity.id_config_information == PointType.STRING.value))
        if point_id and id_device_mppt:
            query = (select(PointListEntity)
                     .where(PointListEntity.id_template == device.id_template)
                     .where(PointListEntity.parent == point_id)
                     .where(PointListEntity.id_config_information == PointType.STRING.value))
        result = await session.execute(query)
        points = result.scalars().all()
        if not points:
            logging.error(f"No string points found for {device.table_name}")
            return

        for point in points:
            result = await session.execute(select(PointListEntity.id)
                                           .where(PointListEntity.id_template == device.id_template)
                                           .where(PointListEntity.parent == point.id)
                                           .where(PointListEntity.id_config_information == PointType.PANEL.value)
                                           .with_only_columns(func.count()))
            count = result.scalar()
            new_device_mppt_string = DeviceMpptStringEntity(**DeviceMpptString(**point.__dict__,
                                                                               id_point_list=point.id,
                                                                               namekey=point.id_pointkey,
                                                                               id_device_list=device.id,
                                                                               panel=count).
                                                            dict(exclude={"id", "parent"}),
                                                            parent=id_device_mppt, )
            session.add(new_device_mppt_string)
            await session.flush()
            await self.add_connection(DeviceConnection(device_list_id=id_device_mppt,
                                                       device_table="device_mppt",
                                                       connect_device_id=new_device_mppt_string.id,
                                                       connect_device_table="device_mppt_string"),
                                      session=session)
            await self.add_device_panel(device, point.id, new_device_mppt_string.id, session=session)

    @async_db_request_handler
    async def add_device_panel(self,
                               device: DeviceModel,
                               point_id: int,
                               id_device_string: int,
                               session: AsyncSession):
        logging.info(f"Adding device panel for {device.table_name}")
        query = (select(PointListEntity)
                 .where(PointListEntity.id_template == device.id_template)
                 .where(PointListEntity.parent == point_id)
                 .where(PointListEntity.id_config_information == PointType.PANEL.value))
        result = await session.execute(query)
        points = result.scalars().all()

        if not points:
            logging.error(f"No panel points found for {device.table_name}")
            return

        for point in points:
            new_panel = DevicePanelEntity(**DevicePanel(**point.__dict__,
                                                        id_point_list=point.id,
                                                        id_device_list=device.id, )
                                          .dict(exclude={"id", "parent"}),
                                          parent=id_device_string)
            session.add(new_panel)
            await session.flush()
            await self.add_connection(DeviceConnection(device_list_id=id_device_string,
                                                       device_table="device_mppt_string",
                                                       connect_device_id=new_panel.id,
                                                       connect_device_table="device_panel"),
                                      session=session)

        logging.info(f"Device panel of {device.table_name} added")

    @async_db_request_handler
    async def add_device_point_list_map(self, device: DeviceModel, session: AsyncSession):
        logging.info(f"Adding device point list map for {device.table_name}")
        query = (select(PointListEntity)
                 .where(PointListEntity.id_template == device.id_template)
                 .where(PointListEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()

        if not points:
            logging.error(f"No points found for {device.table_name}")
            return

        session.add_all([DevicePointListMapEntity(**DevicePointListMap(**point.__dict__,
                                                                       id_point_list=point.id,
                                                                       id_device_list=device.id)
                                                  .dict(exclude={"id"}))
                         for point in points])
        logging.info(f"Device point list map of {device.table_name} added")

    @staticmethod
    @async_db_request_handler
    async def get_devices(session: AsyncSession) -> List[DeviceModel]:
        query = select(DevicesEntity)
        result = await session.execute(query)
        devices = result.scalars().all()

        output = []
        for device in devices:
            communication = device.communication.__dict__ if device.communication else None
            device_type = device.device_type.__dict__ if device.device_type else None
            del device.__dict__["communication"]
            del device.__dict__["device_type"]
            output.append(DeviceModel(**device.__dict__,
                                      communication=communication,
                                      device_type=device_type))
        return output

    @staticmethod
    @async_db_request_handler
    async def get_points(id_template: int, session: AsyncSession) -> List[Point]:
        query = (select(PointListEntity)
                 .where(PointListEntity.id_template == id_template)
                 .order_by(PointListEntity.id))
        result = await session.execute(query)
        points = result.scalars().all()

        mppt_points = [Point(**point.__dict__) for point in points
                       if point.id_config_information != PointType.POINT.value]
        control_group_points = [Point(**point.__dict__) for point in points
                                if point.id_config_information == PointType.POINT.value
                                and point.id_control_group is not None]
        normal_points = [Point(**point.__dict__) for point in points
                         if point.id_config_information == PointType.POINT.value
                         and point.id_control_group is None]
        return normal_points + mppt_points + control_group_points
