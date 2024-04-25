from fastapi import HTTPException, status
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_entity import PointListControlGroup as PointControlGroupEntity
from .point_config_model import PointListControlGroup

from ..point.point_entity import Point as PointEntity
from ..point.point_model import PointBase
from ..point.point_service import PointService
from ..template.template_service import TemplateService
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

    @async_db_request_handler
    async def add_control_group(self, control_group: PointControlGroupEntity, session: AsyncSession):
        id_template = control_group.id_template
        is_exist = await TemplateService().get_template_by_id(id_template, session)

        if not isinstance(is_exist, dict):
            return is_exist

        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id_template == id_template)
                 .where(PointControlGroupEntity.namekey == "".join(control_group.name)))
        result = await session.execute(query)
        if result.scalars().first() is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Control group already exists")

        new_control_group = PointControlGroupEntity(
            **control_group.dict(exclude={"id", "namekey"}, exclude_unset=True),
            namekey="".join(control_group.name)
        )
        session.add(new_control_group)
        await session.commit()
        return new_control_group.__dict__

    @async_db_request_handler
    async def update_control_group(self,
                                   id_control_group: int,
                                   session: AsyncSession,
                                   control_group: PointListControlGroup):
        if control_group.id_template is not None:
            is_exist = await TemplateService().get_template_by_id(control_group.id_template, session)

            if not isinstance(is_exist, dict):
                return is_exist

        query = (update(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id == id_control_group)
                 .values(**control_group.dict(exclude={"id", "namekey"}, exclude_unset=True)))

        await session.execute(query)
        await session.commit()
        return "Updated control group successfully"

    @async_db_request_handler
    async def delete_control_group(self, control_group_id: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_control_group == control_group_id))
        result = await session.execute(query)
        points = result.scalars().all()

        for point in points:
            await PointService().update_point(point.id, session, PointBase(id_control_group=None))

        query = (delete(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id == control_group_id))
        await session.execute(query)
        await session.commit()
        return "Deleted control group successfully"
