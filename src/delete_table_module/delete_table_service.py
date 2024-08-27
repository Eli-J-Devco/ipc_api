import logging

from sqlalchemy import text, MetaData, update, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete

from ..async_db.src.async_db.wrapper import async_db_request_handler
from ..devices_entity import (Devices as DevicesEntity,
                              DeviceMppt as DeviceMpptEntity,
                              DeviceMpptString as DeviceMpptStringEntity,
                              DevicePanel as DevicePanelEntity,
                              DevicePointListMap as DevicePointListMapEntity,
                              DeviceComponent as DeviceComponentEntity, DeviceType, DeviceTypeGroup, )
from ..devices_model import (DeviceModel)
from ..pm2_service.model import DeviceModel as PM2DeviceModel

logger = logging.getLogger(__name__)


class DeleteTableService:
    def __init__(self,
                 metadata: MetaData):
        self.metadata = metadata

    @async_db_request_handler
    async def validate_table(self, device_id: int, table_name: str, session: AsyncSession):
        query = f"SELECT * FROM {table_name} WHERE id_device_list = {device_id}"
        result = await session.execute(text(query))

        if result.scalars().all() == 0:
            logging.info(f"Table {table_name} not found")
            return False

        return True

    @async_db_request_handler
    async def delete_device_mppt(self, device: DeviceModel, session: AsyncSession):
        logging.info(f"Deleting device mppt for {device.table_name}")
        query = (delete(DeviceMpptEntity)
                 .where(DeviceMpptEntity.id_device_list == device.id))
        await session.execute(query)
        await session.commit()
        logging.info(f"Device mppt of {device.table_name} deleted")

    @async_db_request_handler
    async def delete_device_string(self,
                                   device: DeviceModel,
                                   session: AsyncSession):
        logging.info(f"Deleting device string for {device.table_name}")
        query = (delete(DeviceMpptStringEntity)
                 .where(DeviceMpptStringEntity.id_device_list == device.id))
        await session.execute(query)
        await session.commit()
        logging.info(f"Device string of {device.table_name} deleted")

    @staticmethod
    @async_db_request_handler
    async def delete_device_panel(device: DeviceModel,
                                  session: AsyncSession):
        logging.info(f"Deleting device panel for {device.table_name}")
        query = (delete(DevicePanelEntity)
                 .where(DevicePanelEntity.id_device_list == device.id))
        await session.execute(query)
        await session.commit()
        logging.info(f"Device panel of {device.table_name} deleted")

    @async_db_request_handler
    async def delete_device_point_list_map(self, device: DeviceModel, session: AsyncSession):
        logging.info(f"Deleting device point list map for {device.table_name}")
        query = (delete(DevicePointListMapEntity)
                 .where(DevicePointListMapEntity.id_device_list == device.id))
        await session.execute(query)
        await session.commit()
        logging.info(f"Device point list map of {device.table_name} deleted")

    @async_db_request_handler
    async def delete_table(self, table_name: str, session: AsyncSession):
        logging.info(f"Deleting table {table_name}")
        query = f"DROP TABLE IF EXISTS {table_name} CASCADE"
        await session.execute(text(query))
        await session.commit()
        logging.info(f"Table {table_name} deleted")

    @staticmethod
    @async_db_request_handler
    async def delete_device(device_id: int, session: AsyncSession):
        logging.info(f"Deleting device {device_id}")
        query = update(DevicesEntity).where(DevicesEntity.parent == device_id).values(parent=None)
        await session.execute(query)

        query = delete(DevicesEntity).where(DevicesEntity.id == device_id)
        await session.execute(query)
        await session.commit()
        logging.info(f"Device {device_id} deleted")

    @async_db_request_handler
    async def delete_device_component(self, device_id: int, session: AsyncSession) -> list[PM2DeviceModel]:
        """
        Delete device component
        :param device_id:
        :param session:
        :return: list[PM2DeviceModel]
        """
        logging.info(f"Delete device component {device_id}")
        query = select(DevicesEntity).where(DevicesEntity.id == device_id)
        result = await session.execute(query)
        device = result.scalars().first()
        id_device_type = device.id_device_type

        query = (select(DeviceComponentEntity)
                 .where(DeviceComponentEntity.main_type == id_device_type)
                 .where(DeviceComponentEntity.require.__eq__(True)))
        result = await session.execute(query)
        require_type_list = [device_type_group.group for device_type_group in result.scalars().all()]

        logger.info(f"Require type list: {require_type_list}")
        query = (select(DevicesEntity)
                 .join(DeviceType, DevicesEntity.id_device_type == DeviceType.id)
                 .join(DeviceTypeGroup, DeviceType.group == DeviceTypeGroup.id)
                 .where(DevicesEntity.parent == device_id)
                 .where(DeviceTypeGroup.id.in_(require_type_list)))
        logger.info(f"Query: {query}")
        result = await session.execute(query)
        component_list = result.scalars().all()

        logger.info(f"Component list: {component_list}")
        results = []
        for component in component_list:
            logger.info(f"Delete component {component.__dict__}")
            msg = PM2DeviceModel(id=component.id,
                                 name=component.name,
                                 id_communication=component.communication.__dict__.get("id")
                                 if component.communication else None,
                                 connect_type=component.communication.__dict__.get("name")
                                 if component.communication else None,
                                 mode=0,
                                 device_type_value=component.device_type.__dict__.get("type"), )
            await self.delete_device(component.id, session)
            results.append(msg)

        return results
