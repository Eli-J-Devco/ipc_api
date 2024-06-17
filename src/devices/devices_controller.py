# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .components_service import ComponentsService
from .devices_filter import AddDevicesFilter, GetDeviceFilter, UpdateDeviceFilter, AddDeviceGroupFilter, \
    GetDeviceComponentFilter, DeleteDeviceFilter, ListDeviceFilter
from .devices_service import DevicesService
from .devices_utils_service import UtilsService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.pagination_model import Pagination
from ..utils.service_wrapper import ServiceWrapper


@Controller("devices")
class DevicesController:
    def __init__(self, devices_service: DevicesService,
                 components_service: ComponentsService, utils_service: UtilsService):
        self.devices_service = devices_service
        self.components_service = components_service
        self.utils_service = utils_service

    @Post("/get/all/")
    async def get_devices(self,
                          body: ListDeviceFilter,
                          pagination: Pagination = Depends(),
                          session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_devices)(body, session, pagination)

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
                          pagination: Pagination = Depends(),
                          session: AsyncSession = Depends(config.get_db),
                          auth: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.devices_service
                                     .add_devices)(devices, session, pagination))

    @Post("/delete/")
    async def delete_device(self, devices: DeleteDeviceFilter,
                            pagination: Pagination = Depends(),
                            session: AsyncSession = Depends(config.get_db),
                            auth: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.devices_service
                                     .delete_device)(devices, session, pagination))

    @Post("/update/")
    async def update_device(self, device: UpdateDeviceFilter,
                            pagination: Pagination = Depends(),
                            session: AsyncSession = Depends(config.get_db),
                            auth: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.devices_service
                                     .update_device)(device, session, pagination))

    @Post("/config/type/get/")
    async def get_device_type(self, session: AsyncSession = Depends(config.get_db),
                              auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.utils_service.get_device_type)(session)

    @Post("/config/group/get/")
    async def get_device_group(self, session: AsyncSession = Depends(config.get_db),
                               auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.utils_service.get_device_group)(session)

    @Post("/config/group/add/")
    async def add_device_group(self, device_group: AddDeviceGroupFilter,
                               session: AsyncSession = Depends(config.get_db),
                               auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.utils_service.add_device_group)(device_group, session)

    @Post("/point_map/get/")
    async def get_device_point_map(self, device_id: int, session: AsyncSession = Depends(config.get_db),
                                   auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.devices_service.get_device_points)(device_id, session)

    @Post("/component/get/")
    async def get_device_component(self,
                                   device_type: GetDeviceComponentFilter,
                                   session: AsyncSession = Depends(config.get_db),
                                   auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.components_service
                                                  .get_device_components_by_main_type)(device_type, session)

    @Post("/component/get/all/")
    async def get_all_device_component(self,
                                       session: AsyncSession = Depends(config.get_db),
                                       auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.components_service.get_all_device_type_components)(session)

    @Post("/component/")
    async def get_device_components(self,
                                    device_id: int,
                                    session: AsyncSession = Depends(config.get_db),
                                    auth: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.components_service.get_device_components)(device_id, session)
