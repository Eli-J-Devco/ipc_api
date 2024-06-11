# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging

from nest.core import Controller, Post, Depends
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .template_filter import GetTemplateFilter
from ..config import config

from .template_service import TemplateService
from .template_model import TemplateBase
from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication
from ..utils.service_wrapper import ServiceWrapper


@Controller("template")
class TemplateController:

    def __init__(self, template_service: TemplateService):
        self.template_service = template_service

    @Post("/get/")
    async def get_template(self,
                           body: GetTemplateFilter,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.template_service.get_template)(body, session)

    @Post("/get/manual/")
    async def get_manual(self,
                         id_device_type: int,
                         session: AsyncSession = Depends(config.get_db),
                         user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.template_service.get_manual)(id_device_type, session)

    @Post("/config/get/")
    async def get_config(self,
                         session: AsyncSession = Depends(config.get_db),
                         user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.template_service.get_template_config)(session)

    @Post("/config/control_group/")
    async def get_control_group_by_device_type(self,
                                               id_template: int,
                                               session: AsyncSession = Depends(config.get_db),
                                               user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.template_service
                                                  .get_control_group_by_device_type)(session, id_template)

    @Post("/add/")
    async def add_template(self,
                           template: TemplateBase,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        is_template_exist = await (ServiceWrapper
                                   .async_wrapper(self.template_service
                                                  .get_template_by_name)(template.name,
                                                                         template.id_device_group,
                                                                         session))
        if isinstance(is_template_exist, JSONResponse):
            if is_template_exist.status_code != status.HTTP_200_OK:
                return await ServiceWrapper.async_wrapper(self.template_service.add_template)(session, template)

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"message": f"Template with name: {template.name} already exists"})

    @Post("/delete/")
    async def delete_template(self,
                              template: GetTemplateFilter,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.template_service
                                     .get_template_by_id)(template.id,
                                                          session,
                                                          self.template_service.delete_template))
