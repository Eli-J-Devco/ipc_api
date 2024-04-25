import logging

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .point_model import PointBase
from .point_entity import Point as PointEntity, ManualPoint as ManualPointEntity

from ..point_config.point_config_filter import (PointType)
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class PointService:
    @async_db_request_handler
    async def add_point(self,
                        id_point: int | None,
                        session: AsyncSession,
                        id_template: int,
                        point: PointBase | list[PointBase] | dict[str, PointBase] | PointEntity | ManualPointEntity):
        if isinstance(point, list):
            session.add_all([PointEntity(**p.dict(exclude={"id", "register_value"}),
                                         id_template=id_template,
                                         register=p.register_value)
                             for p in point])
            await session.commit()
            return "Points added successfully"

        if isinstance(point, dict):
            new_point = PointEntity(
                **point,
                id_template=id_template,
                register=point["register_value"]
            )
            session.add(new_point)
            await session.commit()
            return "Point added successfully"

        if point.id is not None:
            is_id_exist = await (ServiceWrapper
                                 .async_wrapper(self.get_point_by_id)(point.id,
                                                                      session))
            if isinstance(is_id_exist, dict):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Point already exists")

        if point.id_pointkey is not None:
            is_pointkey_exist = await (ServiceWrapper
                                       .async_wrapper(self.get_point_by_pointkey)(id_template,
                                                                                  point.id_pointkey,
                                                                                  session))
            if isinstance(is_pointkey_exist, dict):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Pointkey already exists")

        new_point = PointEntity(
            **point.dict(exclude={"id", "register_value"}),
            id_template=id_template,
            register=point.register_value
        )
        session.add(new_point)
        await session.commit()
        return "Point added successfully"

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

        return point_entity.__dict__

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

        return point_entity

    @async_db_request_handler
    async def get_points(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType().POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def update_point(self, id_point: int, session: AsyncSession, point: PointBase):
        query = (update(PointEntity)
                 .where(PointEntity.id == id_point)
                 .values(point.dict(exclude_unset=True)))
        await session.execute(query)
        await session.commit()
        return "Point updated successfully"

    @async_db_request_handler
    async def delete_point(self, id_point: int, session: AsyncSession):
        query = (delete(PointEntity)
                 .where(PointEntity.id == id_point))
        await session.execute(query)
        await session.commit()
        return "Point deleted successfully"

    @async_db_request_handler
    async def get_manual_point_list(self, id_device_type: int, session: AsyncSession) -> list[PointBase]:
        query = (select(ManualPointEntity)
                 .where(ManualPointEntity.id_device_type == id_device_type)
                 .where(ManualPointEntity.id_config_information == PointType().POINT)
                 .where(ManualPointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return [PointBase(**point.__dict__) for point in points]
