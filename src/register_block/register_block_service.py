# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging
from typing import Sequence

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from .register_block_filter import AddRegisterBlocksFilter, DeleteRegisterBlockFilter, UpdateRegisterBlockFilter
from .register_block_model import RegisterBlockBase, RegisterBlock, ValidateRegisterBlock
from .register_block_entity import RegisterBlock as RegisterBlockEntity, RegisterBlock

from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_service import ProjectSetupService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class RegisterBlockService:
    def __init__(self, project_setup_service: ProjectSetupService):
        self.project_setup_service = project_setup_service

    @async_db_request_handler
    async def add_register_blocks(self, body: AddRegisterBlocksFilter,
                                  session: AsyncSession) -> Sequence[RegisterBlock]:
        """
        Add register blocks
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: JSONResponse
        """
        last_register_block = await self.get_last_register_block(body.id_template, session)
        if not last_register_block:
            last_register_block = RegisterBlockEntity(id_template=body.id_template)

        register_blocks = []
        for _ in range(body.num_of_register_blocks):
            register_blocks.append(RegisterBlockEntity(**RegisterBlockBase(**last_register_block
                                                                           .__dict__).dict(exclude={"id"})))

        session.add_all(register_blocks)
        await session.commit()
        return await self.get_register_block(body.id_template, session)

    @async_db_request_handler
    async def get_register_block(self, id_template: int, session: AsyncSession) -> Sequence[RegisterBlock]:
        """
        Get register blocks
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: Sequence[RegisterBlock]
        """
        query = (select(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id_template == id_template))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_last_register_block(self, id_template: int, session: AsyncSession) -> RegisterBlockEntity:
        """
        Get last register block
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: RegisterBlockEntity
        """
        query = (select(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id_template == id_template)
                 .order_by(RegisterBlockEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_register_block_by_id(self, id_register_block: int,
                                       session: AsyncSession,
                                       func=None, *args, **kwargs) -> RegisterBlockEntity:
        """
        Get register block by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_register_block:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return: RegisterBlockEntity
        """
        query = (select(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id == id_register_block))
        result = await session.execute(query)
        register_block = result.scalars().first()

        if register_block is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Register block not found")

        if func:
            return await func(register_block, session, *args, **kwargs)

        return register_block.__dict__

    @async_db_request_handler
    async def update_register_blocks(self,
                                     session: AsyncSession,
                                     body: UpdateRegisterBlockFilter) -> Sequence[RegisterBlock]:
        """
        Update register blocks
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param body:
        :return: Sequence[RegisterBlock]
        """
        id_template = body.id_template
        if not id_template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template is required")

        register_blocks = body.register_blocks
        if isinstance(register_blocks, list):
            for block in register_blocks:
                block.id_template = id_template
                await self.update_register_block(block, session)

            return await self.get_register_block(id_template, session)

        register_blocks.id_template = id_template
        await self.update_register_block(register_blocks, session)
        return await self.get_register_block(id_template, session)

    @async_db_request_handler
    async def update_register_block(self, register_block: RegisterBlock,
                                    session: AsyncSession) -> JSONResponse | str:
        """
        Update register block
        :author: nhan.tran
        :date: 20-05-2024
        :param register_block:
        :param session:
        :return: str
        """
        validation = ValidateRegisterBlock(**register_block.dict())
        validated = await (ServiceWrapper
                           .async_wrapper(self.validate_information)(validation,
                                                                     session))
        if isinstance(validated, JSONResponse):
            if validated.status_code != status.HTTP_200_OK:
                return validated

        query = (update(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id == register_block.id)
                 .values(register_block.dict(exclude_unset=True)))
        await session.execute(query)
        await session.commit()

        return "Register block updated successfully"

    @async_db_request_handler
    async def delete_register_blocks(self, body: DeleteRegisterBlockFilter,
                                     session: AsyncSession) -> Sequence[RegisterBlock]:
        """
        Delete register blocks
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: Sequence[RegisterBlock]
        """
        id_template = body.id_template
        if not id_template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template is required")

        id_register_block = body.id_register_block

        if isinstance(id_register_block, list):
            for id_block in id_register_block:
                await ServiceWrapper.async_wrapper(self.delete_register_block)(id_template,
                                                                               id_block,
                                                                               session)
            return await self.get_register_block(id_template, session)

        return await self.delete_register_block(id_template, id_register_block, session)

    @async_db_request_handler
    async def delete_register_block(self, id_template: int,
                                    id_register_block: int,
                                    session: AsyncSession) -> Sequence[RegisterBlock] | JSONResponse:
        """
        Delete register block
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param id_register_block:
        :param session:
        :return: Sequence[RegisterBlock] | JSONResponse
        """
        is_exist = await ServiceWrapper.async_wrapper(self.get_register_block_by_id)(id_register_block, session)

        if isinstance(is_exist, JSONResponse):
            if is_exist.status_code != status.HTTP_200_OK:
                return is_exist

        query = (delete(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id_template == id_template)
                 .where(RegisterBlockEntity.id == id_register_block))
        await session.execute(query)
        await session.commit()

        return await self.get_register_block(id_template, session)

    @async_db_request_handler
    async def validate_information(self,
                                   validation: ValidateRegisterBlock,
                                   session: AsyncSession,
                                   func=None, *args, **kwargs) -> ValidateRegisterBlock | JSONResponse:
        """
        Validate information
        :author: nhan.tran
        :date: 20-05-2024
        :param validation:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return: ValidateRegisterBlock | JSONResponse
        """
        if not validation.id_template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template is required")

        if not validation.id_type_function:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Type function is required")

        config_validation = (ServiceWrapper
                             .sync_wrapper(self.project_setup_service
                                           .validate_config_information)(validation.id_type_function,
                                                                         ConfigInformationType.TYPE_MODBUS_FUNCTION))
        if isinstance(config_validation, JSONResponse):
            if config_validation.status_code == status.HTTP_400_BAD_REQUEST:
                return config_validation

        if func:
            return await func(session, *args, **kwargs)

        return validation

    @async_db_request_handler
    async def get_type_function(self, session: AsyncSession) -> JSONResponse:
        """
        Get type function
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: JSONResponse
        """
        return await (ServiceWrapper
                      .async_wrapper(self.project_setup_service
                                     .get_config_information_by_type)(session,
                                                                      ConfigInformationType.TYPE_MODBUS_FUNCTION))
