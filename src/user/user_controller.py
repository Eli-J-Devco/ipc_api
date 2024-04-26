from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status

from .user_filter import GetUserFilter
from .user_service import UserService
from .user_model import UserCreate, UserUpdate, UserUpdatePassword, UserBase, User
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user

from ..config import config
from ..utils.PaginationModel import Pagination
from ..utils.service_wrapper import ServiceWrapper


@Controller("user")
class UserController:

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @Post("/get/all/")
    async def get_user(self,
                       pagination: Pagination = Depends(),
                       user_filter: GetUserFilter = Depends(),
                       session: AsyncSession = Depends(config.get_db),
                       user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.user_service.get_user)(pagination, session, user_filter)

    @Post("/get/")
    async def get_user_by_id(self,
                             body: User,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.user_service.get_user_by_id)(body.id, session)

    @Post("/add/")
    async def add_user(self, user: UserCreate,
                       session: AsyncSession = Depends(config.get_db),
                       current_user: Authentication = Depends(get_current_user)):
        result = await (ServiceWrapper
                        .async_wrapper(self.user_service
                                       .get_user_by_email)(user.email, session))
        if isinstance(result, JSONResponse):
            if result.status_code == status.HTTP_404_NOT_FOUND:
                return await ServiceWrapper.async_wrapper(self.user_service.add_user)(user, session)
            return result

        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": "User already exists"})

    @Post("/update/")
    async def update_user(self, user: UserUpdate,
                          session: AsyncSession = Depends(config.get_db),
                          current_user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user.id,
                                                      session,
                                                      self.user_service.update_user,
                                                      user))

    @Post("/delete/")
    async def delete_user(self,
                          body: User,
                          session: AsyncSession = Depends(config.get_db),
                          user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(body.id,
                                                      session,
                                                      self.user_service.delete_user,))

    @Post("/activate/")
    async def activate_user(self,
                            body: User,
                            session: AsyncSession = Depends(config.get_db),
                            user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(body.id,
                                                      session,
                                                      self.user_service.activate_user,
                                                      body.id, ))

    @Post("/deactivate/")
    async def deactivate_user(self,
                              body: User,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(body.id,
                                                      session,
                                                      self.user_service.deactivate_user,
                                                      body.id, ))

    @Post("/password/update/")
    async def update_password(self,
                              user: UserUpdatePassword,
                              session: AsyncSession = Depends(config.get_db),
                              current_user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user.id,
                                                      session,
                                                      self.user_service.update_password,
                                                      user, ))

    @Post("/password/reset/")
    async def reset_password(self,
                             body: User,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(body.id,
                                                      session,
                                                      self.user_service.reset_password,))
