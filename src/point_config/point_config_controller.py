from nest.core import Controller, Post, Depends
from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_model import PointListControlGroup
from .point_config_service import PointConfigService

from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("point_config")
class PointConfigController:

    def __init__(self, point_config_service: PointConfigService):
        self.point_config_service = point_config_service

    @Post("/control_group/get/")
    async def get_point_control_group(self,
                                      id_template: int,
                                      session: AsyncSession = Depends(config.get_db),
                                      user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_config_service.get_control_groups)(id_template, session)

    @Post("/control_group/add/")
    async def add_point_control_group(self,
                                      body: PointListControlGroup,
                                      session: AsyncSession = Depends(config.get_db),
                                      user: Authentication = Depends(get_current_user)):
        if body.id is not None:
            is_exist = await ServiceWrapper.async_wrapper(self.point_config_service.get_control_group)(body.id, session)

            if isinstance(is_exist, dict):
                return JSONResponse(status_code=status.HTTP_409_CONFLICT, content="Control group already exists")

        return await ServiceWrapper.async_wrapper(self.point_config_service.add_control_group)(body, session)

    @Post("/control_group/update/")
    async def update_control_group(self,
                                   body: PointListControlGroup,
                                   session: AsyncSession = Depends(config.get_db),
                                   user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_config_service
                                                  .get_control_group)(body.id,
                                                                      session,
                                                                      self.point_config_service.update_control_group,
                                                                      body)

    @Post("/control_group/delete/")
    async def delete_control_group(self,
                                   id_control_group: int,
                                   session: AsyncSession = Depends(config.get_db),
                                   user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_config_service
                                     .get_control_group)(id_control_group,
                                                         session,
                                                         self.point_config_service.delete_control_group))

    @Post("/get/type/")
    async def get_point_type(self,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_config_service.get_point_type)()
