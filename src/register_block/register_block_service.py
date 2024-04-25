import logging

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .register_block_model import RegisterBlockBase, RegisterBlock, ValidateRegisterBlock
from .register_block_entity import RegisterBlock as RegisterBlockEntity

from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_service import ProjectSetupService
from ..template.template_service import TemplateService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class RegisterBlockService:
    def __init__(self, project_setup_service: ProjectSetupService, template_service: TemplateService):
        self.project_setup_service = project_setup_service
        self.template_service = template_service

    @async_db_request_handler
    async def add_register_block(self, session: AsyncSession, register_block: RegisterBlockBase):
        new_register_block = RegisterBlockEntity(
            **register_block.dict(exclude_unset=True)
        )
        session.add(new_register_block)
        await session.commit()
        return new_register_block.__dict__

    @async_db_request_handler
    async def get_register_block(self, id_template: int, session: AsyncSession):
        query = (select(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id_template == id_template))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_register_block_by_id(self, id_register_block: int, session: AsyncSession, func=None, *args, **kwargs):
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
                                     id_register_block: id,
                                     session: AsyncSession,
                                     register_block: RegisterBlock | list[RegisterBlock]):
        if isinstance(register_block, list):
            for block in register_block:
                await self.update_register_block(block, session)

            return "Register blocks updated successfully"

        await self.update_register_block(register_block, session)
        return "Register block updated successfully"

    @async_db_request_handler
    async def update_register_block(self, register_block: RegisterBlock, session: AsyncSession):
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
    async def delete_register_blocks(self, id_register_block: int | list[int], session: AsyncSession):
        if isinstance(id_register_block, list):
            success = []
            rejected = []

            for id_block in id_register_block:
                result = await ServiceWrapper.async_wrapper(self.delete_register_block)(id_block, session)
                if isinstance(result, JSONResponse):
                    if result.status_code != status.HTTP_200_OK:
                        rejected.append(id_block)
                        continue

            return {
                "success": f"{len(success)} register blocks deleted successfully",
                "rejected": f"Register blocks with {', '.join(map(str, rejected))} are not found" if rejected else None
            }

        return await self.delete_register_block(id_register_block, session)

    @async_db_request_handler
    async def delete_register_block(self, id_register_block: int, session: AsyncSession):
        is_exist = await ServiceWrapper.async_wrapper(self.get_register_block_by_id)(id_register_block, session)

        if isinstance(is_exist, JSONResponse):
            if is_exist.status_code != status.HTTP_200_OK:
                return is_exist

        query = (delete(RegisterBlockEntity)
                 .where(RegisterBlockEntity.id == id_register_block))
        await session.execute(query)
        await session.commit()

        return "Register block deleted successfully"

    @async_db_request_handler
    async def validate_information(self,
                                   validation: ValidateRegisterBlock,
                                   session: AsyncSession,
                                   func=None, *args, **kwargs):
        if not validation.id_template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template is required")

        template = await ServiceWrapper.async_wrapper(self.template_service
                                                      .get_template_by_id)(validation.id_template,
                                                                           session)
        if isinstance(template, JSONResponse):
            if template.status_code == status.HTTP_404_NOT_FOUND:
                return template

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
