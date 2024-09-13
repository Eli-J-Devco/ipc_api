import logging

from mqtt_service.model import MessageModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_entity import Devices
from .devices_model import Communication, DeviceType, SymbolicDevice
from .devices_service import DeviceService
from .pm2_service.model import CreateCodeEnum, MessageModel as PM2MessageModel, PayloadModel

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
        symbolic_devices = []
        for device in devices:
            query = (select(Devices)
                     .where(Devices.id == device))
            result = await self.session.execute(query)
            device = result.scalars().first()

            if device.creation_state != -1:
                continue

            if DeviceType(**device.device_type.__dict__).type == 1:
                symbolic_devices.append(SymbolicDevice(**device.__dict__))
                continue

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

        if len(symbolic_devices) > 0:
            msg = PM2MessageModel(CODE="CreateNoLogDev",
                                  PAYLOAD=PayloadModel(device=[device.dict() for device in symbolic_devices]))
            await self.device_service.pm2_service.send(msg)
