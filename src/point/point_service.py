# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Any, Sequence

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update, delete, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from .point_entity import Point as PointEntity, ManualPoint as ManualPointEntity
from .point_filter import DeletePointFilter, AddPointFilter, UpdatePointUnitFilter, AddPointListFilter, ControlInputType
from .point_model import PointBase, PointOutput, PointShort
from ..config import env_config
from ..devices.devices_service import DevicesService
from ..point_config.point_config_filter import (PointType)
from ..project_setup.project_setup_model import ConfigInformationShort
from ..utils.service_wrapper import ServiceWrapper
from ..utils.utils import generate_id


@Injectable
class PointService:
    def __init__(self):
        self.devices_service = DevicesService()

    @async_db_request_handler
    async def add_point(self,
                        session: AsyncSession,
                        point: AddPointFilter | AddPointListFilter) -> PointOutput | list[PointOutput] | bool:
        """
        Add point to the database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param point:
        :return: PointOutput | list[PointOutput] | bool
        """
        if isinstance(point, AddPointListFilter):
            session.add_all([PointEntity(**p.dict(exclude={"id",
                                                           "register_value",
                                                           "id_template",
                                                           }, exclude_unset=True),
                                         id_template=point.id_template,
                                         register=p.register_value)
                             for p in point.point])
            await self.devices_service.update_device_points(point.id_template, session)
            return True

        id_template = point.id_template
        last_point = await self.get_last_point(id_template, session)
        if not last_point:
            last_point = PointBase(register_value=65535)

        session.add_all([PointEntity(**last_point.dict(exclude={"id",
                                                                "name",
                                                                "id_pointkey",
                                                                "id_template",
                                                                "register_value"}, exclude_unset=True),
                                     name=f"New Point {_}",
                                     id_pointkey=f"Point{generate_id(env_config.DEFAULT_ID_LENGTH)}",
                                     id_template=id_template,
                                     register=last_point.register_value, )
                         for _ in range(point.num_of_points)])
        await session.commit()
        await self.devices_service.update_device_points(id_template, session)
        return await self.get_points(id_template, session)

    @async_db_request_handler
    async def get_point_by_id(self,
                              id_point: int,
                              session: AsyncSession,
                              func=None, *args, **kwargs) -> PointOutput | PointEntity | HTTPException:
        """
        Get point by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_point:
        :param session:
        :param func:
        :param args:
        :param kwargs:
        :return: PointOutput | PointEntity | HTTPException
        """
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
    async def get_points(self, id_template: int, session: AsyncSession) -> list[PointEntity]:
        """
        Get points by template ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[PointEntity]
        """
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType().POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return jsonable_encoder(points)

    @async_db_request_handler
    async def get_points_by_template(self, id_template: int, session: AsyncSession) -> Sequence[PointEntity]:
        """
        Get points by template ID
        :author: nhan.tran
        :date: 26-07-2024
        :param id_template:
        :param session:
        :return: Sequence[PointEntity]
        """

        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template))
        result = await session.execute(query)
        points = result.scalars().all()
        return points

    @async_db_request_handler
    async def get_points_short(self, id_template: int, session: AsyncSession) -> list[PointShort]:
        """
        Get points by template ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[PointShort]
        """
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
    async def update_point(self, id_point: int, session: AsyncSession, point: PointBase) -> PointOutput | HTTPException:
        """
        Update point by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_point:
        :param session:
        :param point:
        :return: PointOutput | HTTPException
        """
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
    async def update_point_unit(self, point: UpdatePointUnitFilter, session: AsyncSession) -> str:
        """
        Update point unit by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param point:
        :param session:
        :return: str
        """
        id_point = point.id
        unit = point.unit
        query = (update(PointEntity)
                 .where(PointEntity.id == id_point)
                 .values(id_type_units=unit))
        await session.execute(query)
        await session.commit()
        return "Unit updated successfully"

    @async_db_request_handler
    async def delete_point(self, body: DeletePointFilter, session: AsyncSession) -> list[PointBase] | HTTPException:
        """
        Delete point by ID
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: list[PointBase] | HTTPException
        """
        id_template = body.id_template
        if not id_template:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template ID is required")

        id_points = body.id_points
        device_service = DevicesService()
        if isinstance(id_points, list):
            query = (delete(PointEntity)
                     .where(PointEntity.id_template == id_template)
                     .where(PointEntity.id.in_(id_points)))
            await session.execute(query)
            await session.commit()
            await device_service.update_device_points(id_template, session)
            return await self.get_points(id_template, session)

        query = (delete(PointEntity)
                 .where(PointEntity.id == id_points))
        await session.execute(query)
        await session.commit()
        await device_service.update_device_points(id_template, session)
        return await self.get_points(id_template, session)

    @async_db_request_handler
    async def get_manual_point_list(self, id_device_type: int, session: AsyncSession) -> list[PointBase]:
        """
        Get manual point list by device type
        :author: nhan.tran
        :date: 20-05-2024
        :param id_device_type:
        :param session:
        :return: list[PointBase]
        """
        query = (select(ManualPointEntity)
                 .where(ManualPointEntity.id_device_type == id_device_type)
                 .where(ManualPointEntity.id_config_information == PointType().POINT)
                 .where(ManualPointEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return [PointBase(**point.__dict__) for point in points]

    @async_db_request_handler
    async def get_last_point(self, id_template: int, session: AsyncSession) -> PointBase | None:
        """
        Get the last point by template ID
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: PointBase | None
        """
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType().POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .order_by(PointEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        point = result.scalars().first()
        return PointBase(**point.__dict__) if point else None
