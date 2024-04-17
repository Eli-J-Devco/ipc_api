from .point_model import Point
from .point_entity import Point as PointEntity
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@Injectable
class PointService:

    @async_db_request_handler
    async def add_point(self, point: Point, session: AsyncSession):
        new_point = PointEntity(
            **point.dict()
        )
        session.add(new_point)
        await session.commit()
        return new_point.id

    @async_db_request_handler
    async def get_point(self, session: AsyncSession):
        query = select(PointEntity)
        result = await session.execute(query)
        return result.scalars().all()
