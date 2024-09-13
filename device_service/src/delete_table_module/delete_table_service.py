import logging

from sqlalchemy import text, MetaData, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import delete

from ..async_db.src.async_db.wrapper import async_db_request_handler
from ..devices_entity import (Devices as DevicesEntity,
                              DeviceMppt as DeviceMpptEntity,
                              DeviceMpptString as DeviceMpptStringEntity,
                              DevicePanel as DevicePanelEntity,
                              DevicePointListMap as DevicePointListMapEntity, )
from ..devices_model import (DeviceModel)

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