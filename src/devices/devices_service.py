from .devices_model import Devices
from .devices_entity import Devices as DevicesEntity
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..authentication.authentication_repository import AuthenticationRepository


@Injectable
class DevicesService:
    def __init__(self, auth: AuthenticationRepository):
        self.auth = auth
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
        query = select(DevicesEntity)
        result = await session.execute(query)
        return result.scalars().all()
