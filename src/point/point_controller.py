from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..config import config


from .point_service import PointService
from .point_model import Point
from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication


@Controller("point")
class PointController:

    def __init__(self, point_service: PointService):
        self.point_service = point_service

    @Post("/get/")
    async def get_point(self,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await self.point_service.get_point(session)

    @Post("/add/")
    async def add_point(self, point: Point,
                        session: AsyncSession = Depends(config.get_db),
                        user: Authentication = Depends(get_current_user)):
        return await self.point_service.add_point(point, session)
 