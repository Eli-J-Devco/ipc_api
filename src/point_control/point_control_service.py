import logging

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.encoders import jsonable_encoder

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_control_filter import PointControlAddFilter, PointsControlAddFilter, ControlGroupAddFilter
from .point_control_model import PointControl, PointControlRefresh
from .point_control_entity import PointControl as PointControlEntity
from ..point.point_model import PointBase
from ..point_config.point_config_entity import PointListControlGroup

from ..point_config.point_config_model import PointListControlGroupChildren
from ..point_config.point_config_service import PointConfigService
from ..point.point_service import PointService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class PointControlService:
    def __init__(self, point_service: PointService, point_config_service: PointConfigService):
        self.point_service = point_service
        self.point_config_service = point_config_service

    @async_db_request_handler
    async def get_control_group_point(self, id_template: int, session: AsyncSession):
        control_groups = await self.point_config_service.get_control_groups(id_template, session)
        response = []
        for control_group in control_groups:
            query = (select(PointControlEntity)
                     .where(PointControlEntity.id_template == id_template)
                     .where(PointControlEntity.id_control_group == control_group.id)
                     .where(PointControlEntity.status == 1))
            result = await session.execute(query)
            points = jsonable_encoder(result.scalars().all())
            response.append(PointListControlGroupChildren(**control_group.__dict__, children=points))
        return response

    @async_db_request_handler
    async def update_point_control(self, id_control_group: int, session: AsyncSession, body: PointControlAddFilter):
        id_point = body.id_point

        await (ServiceWrapper
               .async_wrapper(self.point_service
                              .get_point_by_id)(id_point,
                                                session,
                                                self.point_service.update_point,
                                                PointBase(
                                                    id=id_point,
                                                    id_control_group=id_control_group,
                                                )))

        return "Updated point control group successfully"

    @async_db_request_handler
    async def update_points_control(self, id_control_group: int, session: AsyncSession, body: PointsControlAddFilter):
        id_points = body.id_points

        success = []
        rejected = []

        for id_point in id_points:
            result = await (ServiceWrapper
                            .async_wrapper(self.point_service
                                           .get_point_by_id)(id_point,
                                                             session,
                                                             self.point_service.update_point,
                                                             PointBase(
                                                                 id=id_point,
                                                                 id_control_group=id_control_group,
                                                             )))
            if isinstance(result, JSONResponse):
                if result.status_code == status.HTTP_404_NOT_FOUND:
                    rejected.append(id_point)
                else:
                    success.append(id_point)
            else:
                success.append(id_point)

        return {
            "success": f"{len(success)} has been updated successfully",
            "rejected": f"{len(rejected)} has been rejected: {', '.join(map(str, rejected))}. They are not found"
        }

    @async_db_request_handler
    async def get_template_detail(self, id_template: int, session: AsyncSession):
        points = await self.point_service.get_points(id_template, session)
        point_controls = await self.get_control_group_point(id_template, session)

        return PointControlRefresh(points=points, point_controls=point_controls)

    @async_db_request_handler
    async def add_new_control_group(self, body: ControlGroupAddFilter, session: AsyncSession):
        new_group = PointListControlGroup(**PointControl(**body.dict(exclude={"id_points"}))
                                          .dict(exclude_unset=True),
                                          namekey=body.name.replace(" ", ""),
                                          status=1)
        session.add(new_group)
        await session.flush()

        if body.id_points:
            for id_point in body.id_points:
                await self.update_point_control(new_group.id,
                                                session,
                                                PointControlAddFilter(id_control_group=new_group.id,
                                                                      id_point=id_point))

        await session.commit()
        return await self.get_template_detail(new_group.id_template, session)

    @async_db_request_handler
    async def get_points_by_control_group(self, id_control_group: int, session: AsyncSession):
        query = (select(PointControlEntity)
                 .where(PointControlEntity.id_control_group == id_control_group)
                 .where(PointControlEntity.status == 1))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())
