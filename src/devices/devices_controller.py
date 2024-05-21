# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_filter import AddDevicesFilter, GetDeviceFilter, UpdateDeviceFilter, AddDeviceGroupFilter
from .devices_service import DevicesService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.PaginationModel import Pagination
from ..utils.service_wrapper import ServiceWrapper


@Controller("devices")
class DevicesController:
    def __init__(self, devices_service: DevicesService):
        self.devices_service = devices_service

    @Post("/get/all/")
    async def get_devices(self,
                          pagination: Pagination = Depends(),
                          session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_devices)(session, pagination)

    @Post("/get/")
    async def get_devices_by_template(self,
                                      body: GetDeviceFilter,
                                      session: AsyncSession = Depends(config.get_db),
                                      auth: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.devices_service
                                     .get_device_by_condition)(body,
                                                               session))

    @Post("/add/")
    async def add_devices(self,
                          devices: AddDevicesFilter,
                          session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.add_devices)(devices, session)

    @Post("/delete/")
    async def delete_device(self, device_id: int | list[int] = None,
                            session: AsyncSession = Depends(config.get_db),
                            auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.delete_device)(device_id, session)

    @Post("/update/")
    async def update_device(self, device: UpdateDeviceFilter,
                            session: AsyncSession = Depends(config.get_db),
                            auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.update_device)(device, session)

    @Post("/config/type/get/")
    async def get_device_type(self, session: AsyncSession = Depends(config.get_db),
                              auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_device_type)(session)

    @Post("/config/group/get/")
    async def get_device_group(self, session: AsyncSession = Depends(config.get_db),
                               auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_device_group)(session)

    @Post("/config/group/add/")
    async def add_device_group(self, device_group: AddDeviceGroupFilter,
                               session: AsyncSession = Depends(config.get_db),
                               auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.add_device_group)(device_group, session)

    @Post("/point_map/get/")
    async def get_device_point_map(self, device_id: int, session: AsyncSession = Depends(config.get_db),
                                   auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_device_points)(device_id, session)
