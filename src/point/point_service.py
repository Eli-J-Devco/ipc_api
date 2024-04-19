import logging

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_filter import PointType, GetPointFilter
from .point_model import PointBase, MPPTPoint, MPPTString
from .point_entity import Point as PointEntity
from ..point_config.point_config_model import PointListControlGroupChildren
from ..point_config.point_config_service import PointConfigService


@Injectable
class PointService:
    @async_db_request_handler
    async def add_point(self, point: PointBase, session: AsyncSession):
        new_point = PointEntity(
            **point.dict()
        )
        session.add(new_point)
        await session.commit()
        return new_point.id

    @async_db_request_handler
    async def get_point_by_filter(self, body: GetPointFilter, session: AsyncSession):
        GET_POINT_FUNCTION = {
            PointType.POINT: self.get_point,
            PointType.MPPT_POINT: self.get_mppt_point,
            PointType.MPPT_VOLTAGE: self.get_mppt_point,
            PointType.MPPT_CURRENT: self.get_mppt_point,
            PointType.MPPT_STRING: self.get_mppt_point,
            PointType.MPPT_PANEL: self.get_mppt_point,
            PointType.CONTROL_GROUP: self.get_control_group_point
        }

        return await GET_POINT_FUNCTION[body.point_type](body.id_template, session)

    @async_db_request_handler
    async def get_point(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType.POINT)
                 .where(PointEntity.id_control_group.__eq__(None))
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_mppt_point(self, id_template: int, session: AsyncSession):
        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template)
                 .where(PointEntity.id_config_information == PointType.MPPT_POINT)
                 .where(PointEntity.status == 1))
        result = await session.execute(query)
        mppt_points = result.scalars().all()

        response = []
        for point in mppt_points:
            adding_children = MPPTPoint(**point.__dict__, children=[])
            query = (select(PointEntity)
                     .where(PointEntity.id_template == id_template)
                     .where(PointEntity.parent == point.id)
                     .where(PointEntity.status == 1))
            result = await session.execute(query)
            mppt_children = result.scalars().all()

            for child in mppt_children:
                if (child.id_config_information == PointType.MPPT_VOLTAGE or
                        child.id_config_information == PointType.MPPT_CURRENT):
                    adding_children.children.append(PointBase(**child.__dict__))
                    continue

                mppt_child = MPPTString(**child.__dict__, children=[])

                query = (select(PointEntity)
                         .where(PointEntity.id_template == id_template)
                         .where(PointEntity.parent == child.id)
                         .where(PointEntity.status == 1))
                result = await session.execute(query)
                string_children = result.scalars().all()
                mppt_child.children = string_children
                adding_children.children.append(mppt_child)
            response.append(adding_children)

        return response

    @async_db_request_handler
    async def get_control_group_point(self, id_template: int, session: AsyncSession):
        control_groups = await PointConfigService().get_control_groups(id_template, session)
        response = []
        for control_group in control_groups:
            query = (select(PointEntity)
                     .where(PointEntity.id_template == id_template)
                     .where(PointEntity.id_control_group == control_group.id)
                     .where(PointEntity.status == 1))
            result = await session.execute(query)
            points = result.scalars().all()
            response.append(PointListControlGroupChildren(**control_group.__dict__, children=points))
        return response
