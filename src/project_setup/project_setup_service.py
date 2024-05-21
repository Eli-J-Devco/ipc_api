# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Sequence

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .project_setup_entity import (
    ProjectSetup as ProjectSetupEntity, Screen as ScreensEntity,
    ConfigInformation as ConfigInformationEntity, Screen
)
from .project_setup_filter import (ConfigInformationEnum,
                                   UpdateProjectSetupFilter,
                                   UpdateFirstPageLoginFilter,
                                   UpdateConfigInformationType,
                                   UpdateRemoteAccessFilter,
                                   UpdateSearchRTUFilter,
                                   ConfigInformationTypeLang)
from .project_setup_model import ConfigInformationShort, FirstPageOnLogin, RemoteAccessInformation
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class ProjectSetupService:
    @async_db_request_handler
    async def get_project_setup(self, session: AsyncSession) -> ProjectSetupEntity:
        """
        Get project setup
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: ProjectSetupEntity
        """
        query = select(ProjectSetupEntity)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_project_setup_id(self, session: AsyncSession) -> int:
        """
        Get project setup ID
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: int
        """
        query = select(ProjectSetupEntity.id)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_project_setup_by_id(self, project_id: int,
                                      session: AsyncSession, func, *args, **kwargs) -> ProjectSetupEntity:
        """
        Get project setup by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return: ProjectSetupEntity
        """
        if not project_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project ID is required")

        query = select(ProjectSetupEntity.id).where(ProjectSetupEntity.id == project_id)
        result = await session.execute(query)

        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(project_id, session, *args, **kwargs)

        return ProjectSetupEntity(**project.__dict__)

    @async_db_request_handler
    async def update_project(self, project_id: int,
                             session: AsyncSession, project: UpdateProjectSetupFilter) -> UpdateProjectSetupFilter:
        """
        Update project setup
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param project:
        :return: UpdateProjectSetupFilter
        """
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(project.dict(exclude_unset=True)))

        await session.execute(query)
        await session.commit()
        return project

    @async_db_request_handler
    async def get_project_serial_number(self, session: AsyncSession) -> str:
        """
        Get project serial number
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: str
        """
        query = select(ProjectSetupEntity.serial_number)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_config_information_by_type(self, session: AsyncSession,
                                             config_type: str) -> list[ConfigInformationShort]:
        """
        Get config information by type
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param config_type:
        :return: list[ConfigInformationShort]
        """
        config_enum = ConfigInformationEnum().__getattribute__(config_type)
        query = (select(ConfigInformationEntity)
                 .where(ConfigInformationEntity.id_type == config_enum.ID_TYPE)
                 .where(ConfigInformationEntity.id > config_enum.MIN)
                 .where(ConfigInformationEntity.id <= config_enum.MAX)
                 .where(ConfigInformationEntity.status == 1))
        result = await session.execute(query)
        return [ConfigInformationShort(**config.__dict__) for config in result.scalars().all()]

    @async_db_request_handler
    async def get_config_information(self, session: AsyncSession, config_id: int) -> ConfigInformationEntity:
        """
        Get config information
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param config_id:
        :return: ConfigInformationEntity
        """
        query = select(ConfigInformationEntity).where(ConfigInformationEntity.id == config_id)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def update_config_information(self,
                                        project_id: int,
                                        session: AsyncSession,
                                        body: UpdateConfigInformationType,
                                        config_type: str) -> str:
        """
        Update config information
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param body:
        :param config_type:
        :return: str
        """
        query = select(ConfigInformationEntity.id).where(ConfigInformationEntity.id == body.id)
        result = await session.execute(query)
        if not result.scalars().first():
            raise Exception(f"{ConfigInformationTypeLang().__getattribute__(config_type)} not found")

        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return f"Updated {ConfigInformationTypeLang().__getattribute__(config_type)} successfully"

    @staticmethod
    def validate_config_information(config_information_id: int, config_type: str) -> None:
        """
        Validate config information
        :author: nhan.tran
        :date: 20-05-2024
        :param config_information_id:
        :param config_type:
        :return: None
        """
        if not config_information_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"{ConfigInformationTypeLang().__getattribute__(config_type)} is required")

        if not (ConfigInformationEnum()
                        .__getattribute__(config_type).MIN <= config_information_id
                and (config_information_id <= ConfigInformationEnum()
                        .__getattribute__(config_type).MAX)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid {ConfigInformationTypeLang().__getattribute__(config_type).lower()} ID")

    @async_db_request_handler
    async def get_remote_access(self,
                                project_id: int,
                                session: AsyncSession) -> RemoteAccessInformation:
        """
        Get remote access
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :return: RemoteAccessInformation
        """
        query = (select(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id))
        result = await session.execute(query)
        result = result.first()
        return RemoteAccessInformation(**result.__dict__)

    @async_db_request_handler
    async def update_remote_access(self,
                                   project_id: int,
                                   session: AsyncSession,
                                   body: UpdateRemoteAccessFilter) -> str:
        """
        Update remote access
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param body:
        :return: str
        """
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return f"Updated remote access successfully"

    @async_db_request_handler
    async def get_first_page_on_login(self, project_id: int, session: AsyncSession) -> FirstPageOnLogin:
        """
        Get first page on login
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :return: FirstPageOnLogin
        """
        query = select(ProjectSetupEntity.id_first_page_on_login).where(ProjectSetupEntity.id == project_id)
        result = await session.execute(query)

        id_first_page_on_login = result.scalars().first()
        screen = await self.get_screen_by_id(id_first_page_on_login, session)
        return FirstPageOnLogin(**screen.__dict__)

    @async_db_request_handler
    async def update_first_page_on_login(self,
                                         project_id: int,
                                         session: AsyncSession,
                                         body: UpdateFirstPageLoginFilter) -> str:
        """
        Update first page on login
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param body:
        :return: str
        """
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(id_first_page_on_login=body.id_first_page_on_login))
        await session.execute(query)
        await session.commit()
        return f"Updated first page on login successfully"

    @async_db_request_handler
    async def get_screens(self, session: AsyncSession) -> Sequence[ScreensEntity]:
        """
        Get screens
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: Sequence[ScreensEntity]
        """
        query = select(ScreensEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_screen_by_id(self, screen_id: int, session: AsyncSession) -> Screen:
        """
        Get screen by ID
        ScreensEntity
        :param screen_id:
        :param session:
        :return: Screen
        """
        query = select(ScreensEntity).where(ScreensEntity.id == screen_id)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def update_search_rtu(self, project_id: int, session: AsyncSession, body: UpdateSearchRTUFilter) -> str:
        """
        Update search RTU
        :author: nhan.tran
        :date: 20-05-2024
        :param project_id:
        :param session:
        :param body:
        :return: str
        """
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return await self.get_project_setup(session)
