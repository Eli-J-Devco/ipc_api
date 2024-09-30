# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from async_db.wrapper import async_db_request_handler
from .project_setup_entity import (
    ProjectSetup as ProjectSetupEntity, Screen as ScreensEntity,
    ConfigInformation as ConfigInformationEntity, Screen
)
from .project_setup_model import ProjectSetup
class ProjectSetupService:
    @async_db_request_handler
    async def get_project_setup( session: AsyncSession) -> ProjectSetupEntity:
        query = select(ProjectSetupEntity)
        result = await session.execute(query)
        project_setup=result.scalars().first()
        if not project_setup:
            return []
        return ProjectSetup(**project_setup.__dict__)

