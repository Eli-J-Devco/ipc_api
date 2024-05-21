# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Sequence

from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_entity import PointListControlGroup as PointControlGroupEntity, PointListControlGroup


class PointControlGroupConfigService:
    @async_db_request_handler
    async def get_control_groups(self, id_template: id, session: AsyncSession) -> Sequence[PointListControlGroup]:
        """
        Get control groups
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: Sequence[PointListControlGroup]
        """
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id_template == id_template)
                 .where(PointControlGroupEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()
