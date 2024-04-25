from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .point_mppt_service import NormalPointMpptService
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("point_mppt")
class PointMpptController:

    def __init__(self, point_mppt_service: NormalPointMpptService):
        self.point_mppt_service = point_mppt_service

    @Post("/get/")
    async def get_mppt_point(self,
                             id_template: int,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_mppt_service.get_mppt_point)(id_template, session)

    @Post("/get/string/")
    async def get_string_point(self,
                               id_template: int,
                               id_point_mppt: int,
                               session: AsyncSession = Depends(config.get_db),
                               user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service.get_string_point)(id_template,
                                                                               id_point_mppt,
                                                                               session))

    @Post("/get/panel/")
    async def get_panel_point(self,
                              id_template: int,
                              id_point_string: int,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service.get_panel_point)(id_template,
                                                                              id_point_string,
                                                                              session))

    @Post("/get/config/")
    async def get_mppt_config_point(self,
                                    id_template: int,
                                    id_point_mppt: int,
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service.get_mppt_config_point)(id_template,
                                                                                    id_point_mppt,
                                                                                    session))

    @Post("/get/formatted/")
    async def get_mppt_point_formatted(self,
                                       id_template: int,
                                       session: AsyncSession = Depends(config.get_db),
                                       user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_mppt_service.get_mppt_point_formatted)(id_template,
                                                                                       session))
