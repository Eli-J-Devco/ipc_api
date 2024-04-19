from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .upload_channel_service import UploadChannelService
from .upload_channel_model import UploadChannel, UploadChannelConfig

from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("upload_channel")
class UploadChannelController:

    def __init__(self, upload_channel_service: UploadChannelService):
        self.upload_channel_service = upload_channel_service

    @Post("/get/")
    async def get_upload_channel(self,
                                 session: AsyncSession = Depends(config.get_db),
                                 user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.upload_channel_service.get_upload_channel)(session)

    @Post("/config/")
    async def get_configs(self,
                          session: AsyncSession = Depends(config.get_db),
                          user: Authentication = Depends(get_current_user)):
        return await ServiceWrapper.async_wrapper(self.upload_channel_service.get_configs)(session)

    @Post("/update/")
    async def update_upload_channel(self,
                                    body: list[UploadChannelConfig],
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.upload_channel_service
                                     .update_upload_channel)(body,
                                                             session))
