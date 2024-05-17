from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

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

    @Post("/get/type/")
    async def get_point_type(self,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_config_service.get_point_type)()
