# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Controller, Post, Depends
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .role_filter import UpdateRoleScreenFilter
from .role_service import RoleService
from .role_model import RoleBase, RoleCreate, RoleUpdate, RoleScreenMapBase
from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user

from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("role")
class RoleController:

    def __init__(self, role_service: RoleService):
        self.role_service = role_service

    @Post("/get/all/")
    async def get_role(self,
                       session: AsyncSession = Depends(config.get_db),
                       user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.role_service.get_role)(session)

    @Post("/get/")
    async def get_role_by_id(self,
                             role: RoleBase,
                             session: AsyncSession = Depends(config.get_db),
                             user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.role_service.get_role_by_id)(role.id, session)

    @Post("/add/")
    async def add_role(self,
                       role: RoleCreate,
                       session: AsyncSession = Depends(config.get_db),
                       user: Authentication = Depends(get_current_user)):
        result = await (ServiceWrapper.async_wrapper(self.role_service
                                                     .get_role_by_name)(role.name,
                                                                        session, ))

        if isinstance(result, JSONResponse):
            if result.status_code == status.HTTP_404_NOT_FOUND:
                return await ServiceWrapper.async_wrapper(self.role_service.add_role)(role, session)
            return result

        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"message": "Role already exists"})

    @Post("/update/")
    async def update_role(self,
                          role: RoleUpdate,
                          session: AsyncSession = Depends(config.get_db),
                          user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service.get_role_by_id)(role.id,
                                                                       session,
                                                                       self.role_service.update_role,
                                                                       role))

    @Post("/delete/")
    async def delete_role(self,
                          role: RoleBase,
                          session: AsyncSession = Depends(config.get_db),
                          user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service
                                     .get_role_by_id)(role.id,
                                                      session,
                                                      self.role_service.delete_role))

    @Post("/activate/")
    async def activate_role(self,
                            role: RoleBase,
                            session: AsyncSession = Depends(config.get_db),
                            user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service
                                     .get_role_by_id)(role.id,
                                                      session,
                                                      self.role_service.activate_role, ))

    @Post("/deactivate/")
    async def deactivate_role(self,
                              role: RoleBase,
                              session: AsyncSession = Depends(config.get_db),
                              user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service
                                     .get_role_by_id)(role.id,
                                                      session,
                                                      self.role_service.deactivate_role, ))

    @Post("/permission/get/")
    async def get_permission_by_role(self,
                                     role: RoleBase,
                                     session: AsyncSession = Depends(config.get_db),
                                     user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service
                                     .get_role_by_id)(role.id,
                                                      session,
                                                      self.role_service.get_role_permissions, ))

    @Post("/permission/update/")
    async def update_permission_by_role(self,
                                        role_screen: RoleScreenMapBase,
                                        session: AsyncSession = Depends(config.get_db),
                                        user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.role_service
                                     .get_role_by_id)(role_screen.id_role,
                                                      session,
                                                      self.role_service.update_role_permission,
                                                      role_screen))