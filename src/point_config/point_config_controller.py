from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import config

from .point_config_service import PointConfigService
from ..utils.service_wrapper import ServiceWrapper


@Controller("point_config")
class PointConfigController:

    def __init__(self, point_config_service: PointConfigService):
        self.point_config_service = point_config_service

    @Post("/control_group/get/")
    async def get_point_control_group(self,
                                      id_template: int,
                                      session: AsyncSession = Depends(config.get_db)):
        return await ServiceWrapper.async_wrapper(self.point_config_service.get_control_groups)(id_template, session)
