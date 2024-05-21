# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .device_point_filter import GetDevicePointMapFilter, PointActionFilter, AlarmValueUpdateFilter, PointUpdateFilter
from .device_point_service import DevicePointService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("device_point")
class DevicePointController:

    def __init__(self, device_point_service: DevicePointService):
        self.device_point_service = device_point_service

    @Post("/")
    async def get_device_point(self,
                               body: GetDevicePointMapFilter,
                               session: AsyncSession = Depends(config.get_db),
                               auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.get_device_point)(body.id, session)

    @Post("/action/")
    async def point_action(self,
                           body: PointActionFilter,
                           session: AsyncSession = Depends(config.get_db),
                           auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.points_action)(body, session)

    @Post("/alarm/")
    async def update_alarm_value(self,
                                 body: AlarmValueUpdateFilter,
                                 session: AsyncSession = Depends(config.get_db),
                                 auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.update_alarm_values)(body, session)

    @Post("/config/unit/")
    async def get_units(self,
                        session: AsyncSession = Depends(config.get_db),
                        auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.get_units)(session)

    @Post("/config/point/")
    async def update_point(self,
                           body: PointUpdateFilter,
                           session: AsyncSession = Depends(config.get_db),
                           auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.device_point_service.update_point_per_edit)(body, session)
