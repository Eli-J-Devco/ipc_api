from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .device_point_filter import PointActionFilter
from .device_point_model import DevicePoint, DevicePointOutput
from .device_point_entity import DevicePointMap as DevicePointEntity
from ..devices.devices_entity import Devices


@Injectable
class DevicePointService:

    @async_db_request_handler
    async def get_device_point(self, device_id: int, session: AsyncSession):
        query = select(Devices.id_template).where(Devices.id == device_id)
        result = await session.execute(query)
        id_template = result.scalars().first()

        query = select(DevicePointEntity).where(DevicePointEntity.id_device_list == device_id)
        result = await session.execute(query)
        return DevicePointOutput(points=[DevicePoint(**device_point.__dict__)
                                         for device_point in result.scalars().all()],
                                 id_template=id_template)

    @async_db_request_handler
    async def points_action(self, body: PointActionFilter, session: AsyncSession):
        points = body.id_point
        id_device = body.id_device
        status = False if body.action.lower().strip() == "disable" else True
        query = (update(DevicePointEntity)
                 .where(DevicePointEntity.id.in_(points))
                 .values(status=status))
        await session.execute(query)

        if body.id_devices_to_config:
            for device_id in body.id_devices_to_config:
                for point_id in points:
                    await self.point_action_by_device(device_id, point_id, status, session)

        await session.commit()
        return await self.get_device_point(id_device, session)

    @async_db_request_handler
    async def point_action_by_device(self,
                                     device_id: int,
                                     point_id: int,
                                     status: bool,
                                     session: AsyncSession):
        query = select(DevicePointEntity.id_point_list).where(DevicePointEntity.id == point_id)
        result = await session.execute(query)
        point_list = result.scalars().first()

        query = (update(DevicePointEntity)
                 .where(DevicePointEntity.id_device_list == device_id)
                 .where(DevicePointEntity.id_point_list == point_list)
                 .values(status=status))
        await session.execute(query)
