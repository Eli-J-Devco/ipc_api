from nest.core import Controller, Post, Depends
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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
                        id_template: int,
                        point: PointBase,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):

        if point.id is not None:
            is_id_exist = await (ServiceWrapper
                                 .async_wrapper(self.point_service
                                                .get_point_by_id)(point.id,
                                                                  session))
            if isinstance(is_id_exist, dict):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Point already exists")

        if point.id_pointkey is not None:
            is_pointkey_exist = await (ServiceWrapper
                                       .async_wrapper(self.point_service
                                                      .get_point_by_pointkey)(id_template,
                                                                              point.id_pointkey,
                                                                              session))
            if isinstance(is_pointkey_exist, dict):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pointkey already exists")

        return await (ServiceWrapper
                      .async_wrapper(self.point_service
                                     .add_point)(point.id,
                                                 session,
                                                 id_template,
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
                           id_point: int,
                           session: AsyncSession = Depends(config.get_db),
                           user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.point_service
                                     .get_point_by_id)(id_point,
                                                       session,
                                                       self.point_service.delete_point, ))
