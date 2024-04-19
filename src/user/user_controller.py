from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status

from .user_service import UserService
from .user_model import UserCreate, UserUpdate, UserUpdatePassword
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
                       session: AsyncSession = Depends(config.get_db),
                       user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.user_service.get_user)(pagination, session)

    @Post("/get/{user_id}/")
    async def get_user_by_id(self, user_id: int,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.user_service.get_user_by_id)(user_id, session)

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

    @Post("/delete/{user_id}/")
    async def delete_user(self, user_id: int,
                          session: AsyncSession = Depends(config.get_db),
                          user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user_id,
                                                      session,
                                                      self.user_service.delete_user,
                                                      user_id))

    @Post("/activate/{user_id}/")
    async def activate_user(self, user_id: int,
                            session: AsyncSession = Depends(config.get_db),
                            user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user_id,
                                                      session,
                                                      self.user_service.activate_user,
                                                      user_id, ))

    @Post("/deactivate/{user_id}/")
    async def deactivate_user(self, user_id: int,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user_id,
                                                      session,
                                                      self.user_service.deactivate_user,
                                                      user_id, ))

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

    @Post("/password/reset/{user_id}/")
    async def reset_password(self, user_id: int,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.user_service
                                     .get_user_by_id)(user_id,
                                                      session,
                                                      self.user_service.reset_password,))
