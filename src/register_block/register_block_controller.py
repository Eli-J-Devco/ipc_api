from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .register_block_filter import GetRegisterBlockFilter, AddRegisterBlocksFilter, DeleteRegisterBlockFilter, \
    UpdateRegisterBlockFilter
from .register_block_model import RegisterBlockBase, RegisterBlock, ValidateRegisterBlock
from .register_block_service import RegisterBlockService

from ..authentication.authentication_model import Authentication
from ..authentication.authentication_repository import get_current_user
from ..config import config
from ..utils.service_wrapper import ServiceWrapper


@Controller("register_block")
class RegisterBlockController:

    def __init__(self, register_block_service: RegisterBlockService):
        self.register_block_service = register_block_service

    @Post("/get/")
    async def get_register_block(self,
                                 body: GetRegisterBlockFilter,
                                 session: AsyncSession = Depends(config.get_db),
                                 user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .get_register_block)(body.id_template,
                                                          session))

    @Post("/add/")
    async def add_register_block(self,
                                 register_block: AddRegisterBlocksFilter,
                                 session: AsyncSession = Depends(config.get_db),
                                 user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .add_register_blocks)(register_block, session))

    @Post("/update/")
    async def update_register_block(self,
                                    register_block: UpdateRegisterBlockFilter,
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .update_register_blocks)(session,
                                                              register_block))

    @Post("/delete/")
    async def delete_register_block(self,
                                    body: DeleteRegisterBlockFilter,
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .delete_register_blocks)(body,
                                                              session))
