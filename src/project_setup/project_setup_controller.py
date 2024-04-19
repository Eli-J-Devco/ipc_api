from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import config

from .project_setup_service import ProjectSetupService
from .project_setup_filter import (UpdateConfigInformationType,
                                   UpdateRemoteAccessFilter,
                                   UpdateFirstPageLoginFilter,
                                   UpdateProjectSetupFilter,
                                   ProjectBaseFilter,
                                   UpdateSearchRTUFilter, ConfigInformationType, )

from ..authentication.authentication_repository import get_current_user
from ..authentication.authentication_model import Authentication
from ..utils.service_wrapper import ServiceWrapper


@Controller("project_setup")
class ProjectSetupController:

    def __init__(self, project_setup_service: ProjectSetupService):
        self.project_setup_service = project_setup_service

    @Post("/")
    async def get_project_setup(self,
                                session: AsyncSession = Depends(config.get_db),
                                user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.project_setup_service.get_project_setup)(session)

    @Post("/update/")
    async def update_project_setup(self,
                                   body: UpdateProjectSetupFilter,
                                   session: AsyncSession = Depends(config.get_db),
                                   user: Authentication = Depends(get_current_user)):
        return await (
            ServiceWrapper.async_wrapper(self.project_setup_service.update_project)(body.id,
                                                                                    session,
                                                                                    body))

    @Post("/logging_interval/get/")
    async def get_logging_interval(self,
                                   session: AsyncSession = Depends(config.get_db),
                                   user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_config_information_by_type)(session,
                                                                      ConfigInformationType.TYPE_LOGGING_INTERVAL))

    @Post("/logging_interval/update/")
    async def update_logging_interval(self,
                                      body: UpdateConfigInformationType,
                                      session: AsyncSession = Depends(config.get_db),
                                      user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service.get_project_setup_by_id)
                      (body.id,
                       session,
                       self.project_setup_service.update_config_information,
                       body,
                       ConfigInformationType.TYPE_LOGGING_INTERVAL))

    @Post("/remote_access/get/")
    async def get_remote_access(self,
                                body: ProjectBaseFilter,
                                session: AsyncSession = Depends(config.get_db),
                                user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_project_setup_by_id)(body.id,
                                                               session,
                                                               self.project_setup_service.get_remote_access))

    @Post("/remote_access/update/")
    async def update_remote_access(self,
                                   body: UpdateRemoteAccessFilter,
                                   session: AsyncSession = Depends(config.get_db),
                                   user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_project_setup_by_id)(body.id,
                                                               session,
                                                               self.project_setup_service.update_remote_access,
                                                               body))

    @Post("/first_page_on_login/get/")
    async def get_first_page_on_login(self,
                                      body: ProjectBaseFilter,
                                      session: AsyncSession = Depends(config.get_db),
                                      user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_project_setup_by_id)(body.id,
                                                               session,
                                                               self.project_setup_service.get_first_page_on_login))

    @Post("/first_page_on_login/update/")
    async def update_first_page_on_login(self,
                                         body: UpdateFirstPageLoginFilter,
                                         session: AsyncSession = Depends(config.get_db),
                                         user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_project_setup_by_id)(body.id,
                                                               session,
                                                               self.project_setup_service.update_first_page_on_login,
                                                               body))

    @Post("/update_search_rtu/")
    async def update_search_rtu(self,
                                body: UpdateSearchRTUFilter,
                                session: AsyncSession = Depends(config.get_db),
                                user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_project_setup_by_id)(body.id,
                                                               session,
                                                               self.project_setup_service.update_search_rtu,
                                                               body))
