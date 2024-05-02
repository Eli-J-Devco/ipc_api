from nest.core import Controller, Post, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .point_filter import DeletePointFilter, AddPointFilter
from .point_model import PointBase
from .point_service import PointService

from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication
from ..utils.service_wrapper import ServiceWrapper
from ..config import config


@Controller("point")
class PointController:

    def __init__(self, point_service: PointService):
        self.point_service = point_service

    @Post("/get/")
    async def get_point(self,
                        id_template: int,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_service.get_points)(id_template, session)

    @Post("/add/")
    async def add_point(self,
                        point: AddPointFilter,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):

        return await (ServiceWrapper
                      .async_wrapper(self.point_service
                                     .add_point)(session,
                                                 point, ))

    @Post("/update/")
    async def update_point(self,
                           point: PointBase,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_service
                                     .get_point_by_id)(point.id,
                                                       session,
                                                       self.point_service.update_point,
                                                       point, ))

    @Post("/delete/")
    async def delete_point(self,
                           body: DeletePointFilter,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_service.delete_point)(body, session))
