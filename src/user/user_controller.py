from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import config


from .user_service import UserService
from .user_model import User


@Controller("user")
class UserController:

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @Get("/")
    async def get_user(self, session: AsyncSession = Depends(config.get_db)):
        return await self.user_service.get_user(session)

    @Post("/")
    async def add_user(self, user: User, session: AsyncSession = Depends(config.get_db)):
        return await self.user_service.add_user(user, session)
 