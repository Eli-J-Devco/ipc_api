from fastapi import HTTPException, status
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_entity import PointListControlGroup as PointControlGroupEntity
from ..utils.service_wrapper import ServiceWrapper


class PointControlGroupConfigService:
    @async_db_request_handler
    async def get_control_groups(self, id_template: id, session: AsyncSession):
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id_template == id_template)
                 .where(PointControlGroupEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_control_group(self, control_group_id: int, session: AsyncSession, func=None, *args, **kwargs):
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id == control_group_id))
        result = await session.execute(query)
        control_group = result.scalars().first()
        if control_group is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control group not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(control_group_id, session, *args, **kwargs)

        return control_group.__dict__

