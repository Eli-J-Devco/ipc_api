import base64
import datetime
import json
import logging
import uuid

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from mqtt_service.mqtt import Publisher
from mqtt_service.model import MessageModel, Topic, MetaData

from .devices_filter import AddDevicesFilter, IncreaseMode, CodeEnum
from .devices_model import Devices, DeviceFull, Action
from .devices_entity import (Devices as DevicesEntity,
                             DeviceType as DeviceTypeEntity,
                             DeviceGroup as DeviceGroupEntity,
                             DevicePointMap as DevicePointMapEntity,)
from ..project_setup.project_setup_service import ProjectSetupService


@Injectable
class DevicesService:
    def __init__(self):
        self.sender = Publisher(
            host="localhost",
            port=1883,
            subscriptions=[f"devices/create"],
            client_id=f"publisher-creating-{uuid.uuid4()}",
            will_qos=2
        )

    @async_db_request_handler
    async def get_devices(self, session: AsyncSession):
        query = (select(DevicesEntity)
                 .where(DevicesEntity.status.__eq__(True)))
        result = await session.execute(query)
        devices = result.scalars().all()

        output = []
        for device in devices:
            driver_type = device.communication.__dict__.get("name")
            output.append(DeviceFull(**device.__dict__,
                                     driver_type=driver_type))

        return output

    @async_db_request_handler
    async def get_device_by_id(self, device_id: int, session: AsyncSession):
        query = select(DevicesEntity).filter(DevicesEntity.id == device_id)
        result = await session.execute(query)
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devices not found")

        return Devices(**device.__dict__)

    @async_db_request_handler
    async def get_device_type_by_device_group(self, id_device_group: int, session: AsyncSession):
        query = select(DeviceGroupEntity.id_device_type).filter(DeviceGroupEntity.id == id_device_group)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_device_type(self, session: AsyncSession):
        query = select(DeviceTypeEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_device_group(self, session: AsyncSession):
        query = select(DeviceGroupEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_communication(self, session: AsyncSession):
        query = select(DevicesEntity.id_communication).distinct()
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def add_devices(self, body: AddDevicesFilter, session: AsyncSession):
        devices = []
        logging.info(f"Rate power: {body.rated_power}")
        for _ in range(body.num_of_devices):
            new_devices = DevicesEntity(
                **DeviceFull(
                    **body.dict(exclude_unset=True, exclude={"rtu_bus_address", "tcp_gateway_port"}),
                    rtu_bus_address=body.rtu_bus_address + (_ if body.inc_mode == IncreaseMode.RTU else 0),
                    tcp_gateway_port=body.tcp_gateway_port + (_ if body.inc_mode == IncreaseMode.TCP else 0),
                    rated_power_custom=body.rated_power,
                ).dict(exclude_none=True)
            )
            session.add(new_devices)
            await session.flush()

            tg = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y%m%d"
            )

            query = (update(DevicesEntity)
                     .where(DevicesEntity.id == new_devices.id)
                     .values(table_name=f"dev_{new_devices.id}",
                             view_table=f"dev_{new_devices.id}_{tg}"))

            await session.execute(query)
            devices.append(new_devices.id)
        await session.commit()

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        code = CodeEnum.CreateRS485Dev.name if body.id_communication < 3 else CodeEnum.CreateTCPDev.name
        creating_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=f"{serial_number}/{Action.CREATE.value}",
                        failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
            message={"type": Action.CREATE.value,
                     "code": code,
                     "devices": devices}
        )
        await self.sender.start()
        self.sender.send(f"{serial_number}/{Action.CREATE.value}",
                         base64.b64encode(json.dumps(creating_msg.dict()).encode("ascii")))
        await self.sender.stop()
        return await self.get_devices(session)

    @async_db_request_handler
    async def delete_device(self, device_id: int | list[int], session: AsyncSession):
        if isinstance(device_id, int):
            device_id = [device_id]
        serial_number = await ProjectSetupService().get_project_serial_number(session)
        del_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=f"{serial_number}/{Action.DELETE.value}",
                        failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
            message={"type": Action.DELETE.value,
                     "code": CodeEnum.DeleteDev.name,
                     "devices": device_id}
        )
        await self.sender.start()
        self.sender.send(f"{serial_number}/{Action.DELETE.value}",
                         base64.b64encode(json.dumps(del_msg.dict()).encode("ascii")))
        await self.sender.stop()

        return await self.get_devices(session)

    @async_db_request_handler
    async def get_device_points(self, device_id: int, session: AsyncSession):
        query = select(DevicePointMapEntity).filter(DevicePointMapEntity.id_device_list == device_id)
        result = await session.execute(query)
        points = result.scalars().all()

        return points
