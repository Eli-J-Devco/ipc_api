from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .device_point_filter import GetDevicePointMapFilter, PointActionFilter
from .device_point_service import DevicePointService
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("device_point")
class DevicePointController:

    def __init__(self, device_point_service: DevicePointService):
        self.device_point_service = device_point_service

    @Post("/")
    async def get_device_point(self,
                               body: GetDevicePointMapFilter,
                               session: AsyncSession = Depends(config.get_db)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.get_device_point)(body.id, session)

    @Post("/action/")
    async def disable_points(self,
                             body: PointActionFilter,
                             session: AsyncSession = Depends(config.get_db)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.points_action)(body, session)

 