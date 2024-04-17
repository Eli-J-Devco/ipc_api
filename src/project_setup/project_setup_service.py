import logging
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import JSONResponse
from fastapi import HTTPException, status

from .project_setup_filter import (ConfigInformationEnum,
                                   UpdateProjectSetupFilter,
                                   UpdateFirstPageLoginFilter,
                                   UpdateLoggingIntervalFilter,
                                   UpdateRemoteAccessFilter,
                                   UpdateSearchRTUFilter)
from .project_setup_model import TypeLoggingInterval
from .project_setup_entity import (
    ProjectSetup as ProjectSetupEntity, Screen as ScreensEntity,
    ConfigInformation as ConfigInformationEntity
)
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class ProjectSetupService:
    @async_db_request_handler
    async def get_project_setup(self, session: AsyncSession):
        query = select(ProjectSetupEntity)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_project_setup_id(self, session: AsyncSession):
        query = select(ProjectSetupEntity.id)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_project_setup_by_id(self, project_id: int, session: AsyncSession, func, *args, **kwargs):
        query = select(ProjectSetupEntity.id).where(ProjectSetupEntity.id == project_id)
        result = await session.execute(query)

        project = result.scalars().first()
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(project_id, session, *args, **kwargs)

        return project

    @async_db_request_handler
    async def update_project(self, project_id: int, session: AsyncSession, project: UpdateProjectSetupFilter):
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(project.__dict__))

        await session.execute(query)
        await session.commit()
        return project

    @async_db_request_handler
    async def get_logging_interval(self, session: AsyncSession):
        query = (select(ConfigInformationEntity.id,
                        ConfigInformationEntity.namekey)
                 .where(ConfigInformationEntity.id > ConfigInformationEnum.TYPE_LOGGING_INTERVAL.MIN)
                 .where(ConfigInformationEntity.id <= ConfigInformationEnum.TYPE_LOGGING_INTERVAL.MAX))
        result = await session.execute(query)
        return [TypeLoggingInterval(
            id=row[0],
            namekey=row[1],
        ) for row in result.all()]

    @async_db_request_handler
    async def update_logging_interval(self, project_id: int, session: AsyncSession, body: UpdateLoggingIntervalFilter):
        query = select(ConfigInformationEntity.id).where(ConfigInformationEntity.id == body.id_logging_interval)
        result = await session.execute(query)
        if not result.scalars().first():
            raise Exception("Logging interval not found")

        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return JSONResponse(status_code=200, content={"message": "Updated logging interval successfully"})

    @async_db_request_handler
    async def get_remote_access(self,
                                project_id: int,
                                session: AsyncSession):
        query = (select(ProjectSetupEntity.allow_remote_access,
                        ProjectSetupEntity.link_remote_access)
                 .where(ProjectSetupEntity.id == project_id))
        result = await session.execute(query)
        result = result.first()
        return JSONResponse(status_code=200,
                            content={
                                "link_remote_access": result[1],
                                "allow_remote_access": True if result[0] == 1 else False
                            })

    @async_db_request_handler
    async def update_remote_access(self,
                                   project_id: int,
                                   session: AsyncSession,
                                   body: UpdateRemoteAccessFilter):
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return JSONResponse(status_code=200, content={"message": "Updated remote access successfully"})

    @async_db_request_handler
    async def get_first_page_on_login(self, project_id: int, session: AsyncSession):
        query = select(ProjectSetupEntity.id_first_page_on_login).where(ProjectSetupEntity.id == project_id)
        result = await session.execute(query)

        id_first_page_on_login = result.scalars().first()
        screen = await self.get_screen_by_id(id_first_page_on_login, session)
        return JSONResponse(status_code=200,
                            content={
                                "screen_name": screen.screen_name,
                                "description": screen.description,
                                "path": screen.path
                            })

    @async_db_request_handler
    async def update_first_page_on_login(self, project_id: int, session: AsyncSession, body: UpdateFirstPageLoginFilter):
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(id_first_page_on_login=body.id_first_page_on_login))
        await session.execute(query)
        await session.commit()
        return JSONResponse(status_code=200, content={"message": "Updated first page on login successfully"})

    @async_db_request_handler
    async def get_screens(self, session: AsyncSession):
        query = select(ScreensEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_screen_by_id(self, screen_id: int, session: AsyncSession):
        query = select(ScreensEntity).where(ScreensEntity.id == screen_id)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def update_search_rtu(self, project_id: int, session: AsyncSession, body: UpdateSearchRTUFilter):
        query = (update(ProjectSetupEntity)
                 .where(ProjectSetupEntity.id == project_id)
                 .values(body.__dict__))
        await session.execute(query)
        await session.commit()
        return await self.get_project_setup(session)
