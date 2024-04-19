from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_model import Devices
from .devices_entity import Devices as DevicesEntity


@Injectable
class DevicesService:

    @async_db_request_handler
    async def add_devices(self, devices: Devices, session: AsyncSession):
        new_devices = DevicesEntity(
            **devices.dict()
        )
        session.add(new_devices)
        await session.commit()
        return new_devices.id

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
