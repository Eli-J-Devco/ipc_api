from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# from .point_config_model import PointConfig
from .point_config_entity import PointListControlGroup as PointControlGroupEntity


@Injectable
class PointConfigService:
    @async_db_request_handler
    async def get_control_groups(self, id_template: id, session: AsyncSession):
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id_template == id_template)
                 .where(PointControlGroupEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def add_control_group(self, control_group: PointControlGroupEntity, session: AsyncSession):
        new_control_group = PointControlGroupEntity(
            **control_group.dict()
        )
        session.add(new_control_group)
        await session.commit()
        return new_control_group.id

    @async_db_request_handler
    async def update_control_group(self, control_group: PointControlGroupEntity, session: AsyncSession):
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id == control_group.id))
        result = await session.execute(query)
        old_control_group = result.scalars().first()
        for key, value in control_group.dict().items():
            setattr(old_control_group, key, value)
        await session.commit()
        return old_control_group.id

    @async_db_request_handler
    async def delete_control_group(self, control_group_id: int, session: AsyncSession):
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id == control_group_id))
        result = await session.execute(query)
        control_group = result.scalars().first()
        await session.delete(control_group)
        await session.commit()
        return control_group.id
