from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .point_filter import GetPointFilter
from ..config import config


from .point_service import PointService
from .point_model import PointBase
from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication
from ..utils.service_wrapper import ServiceWrapper


@Controller("point")
class PointController:

    def __init__(self, point_service: PointService):
        self.point_service = point_service

    @Post("/get/")
    async def get_point(self,
                        body: GetPointFilter = Depends(),
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.point_service.get_point_by_filter)(body, session)

    @Post("/add/")
    async def add_point(self, point: PointBase,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await self.point_service.add_point(point, session)
 