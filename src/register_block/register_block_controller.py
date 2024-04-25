from nest.core import Controller, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .register_block_filter import GetRegisterBlockFilter
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
                                 register_block: RegisterBlockBase,
                                 session: AsyncSession = Depends(config.get_db),
                                 user: Authentication = Depends(get_current_user)):
        validation = ValidateRegisterBlock(**register_block.dict(exclude_unset=True))
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .validate_information)(validation,
                                                            session,
                                                            self.register_block_service.add_register_block,
                                                            register_block))

    @Post("/update/")
    async def update_register_block(self,
                                    register_block: RegisterBlock | list[RegisterBlock],
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .get_register_block_by_id)(register_block.id,
                                                                session,
                                                                self.register_block_service.update_register_blocks,
                                                                register_block))

    @Post("/delete/")
    async def delete_register_block(self,
                                    id_register_block: int | list[int],
                                    session: AsyncSession = Depends(config.get_db),
                                    user: Authentication = Depends(get_current_user)):
        return await (ServiceWrapper
                      .async_wrapper(self.register_block_service
                                     .delete_register_blocks)(id_register_block,
                                                              session))
