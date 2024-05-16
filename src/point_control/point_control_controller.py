from typing import Optional

from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .point_control_filter import PointControlAddFilter, PointsControlAddFilter, ControlGroupAddFilter
from .point_control_service import PointControlService

from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..point_config.point_config_service import PointConfigService
from ..utils.service_wrapper import ServiceWrapper


@Controller("point_control")
class PointControlController:

    def __init__(self, point_control_service: PointControlService):
        self.point_control_service = point_control_service

    @Post("/get/")
    async def get_control_group_point(self,
                                      id_template: int,
                                      session: AsyncSession = Depends(config.get_db),
                                      user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_control_service
                                                  .get_control_group_point)(id_template, session)

    @Post("/add/")
    async def add_new_control_group(self,
                                    body: ControlGroupAddFilter,
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_control_service
                                                  .add_new_control_group)(body, session)
