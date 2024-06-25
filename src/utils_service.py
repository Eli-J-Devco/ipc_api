import logging

from mqtt_service.model import MessageModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.devices_entity import Devices
from src.devices_model import Communication
from src.devices_service import DeviceService
from src.pm2_service.model import CreateCodeEnum

logger = logging.getLogger(__name__)


class UtilsService:
    def __init__(self, device_service: DeviceService,
                 session: AsyncSession = None, ):
        self.device_service = device_service
        self.session = session

    async def handler(self, data: MessageModel):
        logger.info(f"Retrieve data: {data.dict()}")
        devices = data.message.get("devices")
        driver_list = {}

        for device in devices:
            query = (select(Devices)
                     .where(Devices.id == device))
            result = await self.session.execute(query)
            device = result.scalars().first()
            com = Communication(**device.communication.__dict__)
            if com.id_driver_list in driver_list:
                driver_list[com.id_driver_list].append(device.id)
            else:
                driver_list[com.id_driver_list] = [device.id]

        logger.info(f"Driver list: {driver_list}")
        for driver in driver_list:
            msg = MessageModel(**data.dict())
            msg.message["devices"] = driver_list[driver]
            msg.message["code"] = CreateCodeEnum(driver).name
            logger.info(f"Send message: {msg.dict()}")
            await self.device_service.handler(msg)
