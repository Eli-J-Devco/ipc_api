import logging
import time

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .point_filter import DeletePointFilter, AddPointFilter, UpdatePointUnitFilter
from .point_model import PointBase, PointOutput, PointShort
from .point_entity import Point as PointEntity, ManualPoint as ManualPointEntity

from ..point_config.point_config_filter import (PointType)
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class PointService:
    @async_db_request_handler
    async def add_point(self,
                        session: AsyncSession,
                        point: AddPointFilter):
        id_template = point.id_template
        last_point = await self.get_last_point(id_template, session)
        last_index = last_point.id if last_point else 0
        if not last_point:
            last_point = PointBase(register_value=65535)

        session.add_all([PointEntity(**last_point.dict(exclude={"id",
                                                                "name",
                                                                "id_pointkey",
                                                                "id_template",
                                                                "register_value"}, exclude_unset=True),
                                     name=f"Point {_ + last_index}",
                                     id_pointkey=f"Point{_ + last_index}",
                                     id_template=id_template,
                                     register=last_point.register_value, )
                         for _ in range(point.num_of_points)])
        await session.commit()
        return await self.get_points(id_template, session)

    @async_db_request_handler
    async def get_point_by_id(self,
                              id_point: int,
                              session: AsyncSession,
                              func=None, *args, **kwargs):
        query = (select(PointEntity)
                 .where(PointEntity.id == id_point))
        result = await session.execute(query)
        point_entity = result.scalars().first()
        if point_entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Point not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(id_point, session, *args, **kwargs)

        await session.refresh(point_entity)
        return PointOutput(**jsonable_encoder(point_entity))

    @async_db_request_handler
    async def get_point_by_pointkey(self,
                                    id_template: int,
                                    pointkey: str,
                                    session: AsyncSession,
                                    func=None, *args, **kwargs):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_pointkey == pointkey))

        result = await session.execute(query)
        point_entity = result.scalars().first()
        if point_entity is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Point not found")

        if func:
            return await ServiceWrapper.async_wrapper(func)(id_template, session, *args, **kwargs)

        await session.refresh(point_entity)
        return point_entity

    @async_db_request_handler
    async def get_points(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType().POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return jsonable_encoder(points)

    @async_db_request_handler
    async def get_points_short(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()

        output = []
        for point in points:
            output.append(PointShort(**point.__dict__))

        return output

    @async_db_request_handler
    async def update_point(self, id_point: int, session: AsyncSession, point: PointBase):
        updating_point = point.dict(exclude_unset=True, exclude={"id", "register_value"})
        updating_point["register"] = point.register_value

        query = (update(PointEntity)
                 .where(PointEntity.id == id_point)
                 .values(**updating_point))
        await session.execute(query)

        updated_point = await self.get_point_by_id(id_point, session)
        await session.commit()

        return updated_point

    @async_db_request_handler
    async def update_point_unit(self, point: UpdatePointUnitFilter, session: AsyncSession):
        id_point = point.id
        unit = point.unit
        query = (update(PointEntity)
                 .where(PointEntity.id == id_point)
                 .values(id_type_units=unit))
        await session.execute(query)
        await session.commit()
        return "Unit updated successfully"

    @async_db_request_handler
    async def delete_point(self, body: DeletePointFilter, session: AsyncSession):
        id_template = body.id_template
        if not id_template:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template ID is required")

        id_points = body.id_points

        if isinstance(id_points, list):
            query = (delete(PointEntity)
                     .where(PointEntity.id_template == id_template)
                     .where(PointEntity.id.in_(id_points)))
            await session.execute(query)
            await session.commit()
            return await self.get_points(id_template, session)

        query = (delete(PointEntity)
                 .where(PointEntity.id == id_points))
        await session.execute(query)
        await session.commit()
        return await self.get_points(id_template, session)

    @async_db_request_handler
    async def get_manual_point_list(self, id_device_type: int, session: AsyncSession) -> list[PointBase]:
        query = (select(ManualPointEntity)
                 .where(ManualPointEntity.id_device_type == id_device_type)
                 .where(ManualPointEntity.id_config_information == PointType().POINT)
                 .where(ManualPointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return [PointBase(**point.__dict__) for point in points]

    @async_db_request_handler
    async def get_last_point(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType().POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .order_by(PointEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        point = result.scalars().first()
        return PointBase(**point.__dict__) if point else None
