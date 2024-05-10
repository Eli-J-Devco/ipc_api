import base64
import datetime
import json
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
        return result.scalars().all()

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
        for _ in range(body.num_of_devices):
            new_devices = DevicesEntity(
                **DeviceFull(
                    name=body.name,
                    id_device_type=body.id_device_type,
                    id_template=body.id_template,
                    id_communication=body.id_communication,
                    device_virtual=body.device_virtual,
                    rtu_bus_address=body.rtu_bus_address + (_ if body.mode == IncreaseMode.RTU else 0),
                    tcp_gateway_ip=body.tcp_gateway_ip,
                    tcp_gateway_port=body.tcp_gateway_port + (_ if body.mode == IncreaseMode.TCP else 0),
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

        code = CodeEnum.CreateRS485Dev.name if body.id_communication < 3 else CodeEnum.CreateTCPDev.name
        creating_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=Action.CREATE.value, failed=Action.DEAD_LETTER.value),
            message={"type": Action.CREATE.value,
                     "code": code,
                     "devices": devices}
        )
        await self.sender.start()
        self.sender.send(Action.CREATE.value, base64.b64encode(json.dumps(creating_msg.dict()).encode("ascii")))
        await self.sender.stop()
        return await self.get_devices(session)

    @async_db_request_handler
    async def delete_device(self, device_id: int | list[int], session: AsyncSession):
        if isinstance(device_id, int):
            device_id = [device_id]

        del_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=Action.DELETE.value, failed=Action.DEAD_LETTER.value),
            message={"type": Action.DELETE.value,
                     "code": CodeEnum.DeleteDev.name,
                     "devices": device_id}
        )
        await self.sender.start()
        self.sender.send(Action.DELETE.value, base64.b64encode(json.dumps(del_msg.dict()).encode("ascii")))
        await self.sender.stop()

        return await self.get_devices(session)

    @async_db_request_handler
    async def get_device_points(self, device_id: int, session: AsyncSession):
        query = select(DevicePointMapEntity).filter(DevicePointMapEntity.id_device_list == device_id)
        result = await session.execute(query)
        points = result.scalars().all()

        return points