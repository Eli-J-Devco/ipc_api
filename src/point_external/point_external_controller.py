# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .point_external_filter import AddMPPTFilter, AddStringFilter, AddPanelFilter, DeletePointFilter
from .point_external_normal_service import NormalPointExternalService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("point_external")
class PointExternalController:

    def __init__(self, point_mppt_service: NormalPointExternalService):
        self.point_mppt_service = point_mppt_service

    @Post("/add/")
    async def add_point(self,
                        point: AddMPPTFilter,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service
                                     .add_mppt_point)(session,
                                                      point, ))

    @Post("/add/string/")
    async def add_string(self,
                         point: AddStringFilter,
                         session: AsyncSession = Depends(config.get_db),
                         user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service
                                     .add_string)(session,
                                                  point,
                                                  last_mppt_id=point.parent, ))

    @Post("/add/panel/")
    async def add_panel(self,
                        point: AddPanelFilter,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service
                                     .add_panel)(session,
                                                 point,
                                                 last_string_id=point.parent, ))

    @Post("/delete/")
    async def delete_point(self,
                           point: DeletePointFilter,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service
                                     .delete_point)(session,
                                                    point, ))

    @Post("/get/")
    async def get_point(self,
                        template_id: int,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper.async_wrapper(self.point_mppt_service.get_mppt_point)(template_id, session))