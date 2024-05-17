import logging

from fastapi import status, HTTPException
from fastapi.encoders import jsonable_encoder
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from .point_control_entity import PointControl as PointControlEntity
from .point_control_filter import PointControlAddFilter, ControlGroupAddFilter, \
    ControlGroupUpdateFilter, ControlGroupDeleteFilter, PointRemoveFilter, PointsControlAddFilter, \
    PointControlCreateFilter
from .point_control_model import PointControl, PointControlRefresh
from ..point.point_model import PointBase
from ..point.point_service import PointService
from ..point_config.point_config_entity import PointListControlGroup
from ..point_config.point_config_model import PointListControlGroupChildren
from ..point_config.point_config_service import PointConfigService
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
    async def add_existing_point_to_group(self, id_control_group: int,
                                          session: AsyncSession,
                                          body: PointControlAddFilter | PointsControlAddFilter):
        if isinstance(body, PointControlAddFilter):
            id_points = [body.id_point]
        else:
            id_points = body.id_points

        for id_point in id_points:
            await (ServiceWrapper
                   .async_wrapper(self.point_service
                                  .get_point_by_id)(id_point,
                                                    session,
                                                    self.point_service.update_point,
                                                    PointBase(
                                                        id=id_point,
                                                        id_control_group=id_control_group,
                                                    )))
        if isinstance(body, PointsControlAddFilter):
            return await self.get_template_detail(body.id_template, session)

    @async_db_request_handler
    async def get_template_detail(self, id_template: int, session: AsyncSession):
        points = await self.point_service.get_points(id_template, session)
        point_controls = await self.get_control_group_point(id_template, session)

        return PointControlRefresh(points=points, point_controls=point_controls)

    @async_db_request_handler
    async def remove_point_from_control_group(self, body: PointRemoveFilter, session: AsyncSession):
        query = (update(PointControlEntity)
                 .where(PointControlEntity.id.in_(body.id_points))
                 .values(id_control_group=None))
        await session.execute(query)
        await session.commit()
        return await self.get_template_detail(body.id_template, session)

    @async_db_request_handler
    async def create_new_point_to_group(self,
                                        body: PointControlCreateFilter,
                                        session: AsyncSession):
        query = (select(PointListControlGroup)
                 .where(PointListControlGroup.id_template == body.id_template)
                 .where(PointListControlGroup.id == body.id_control_group))
        result = await session.execute(query)
        control_group = result.scalars().first()
        if control_group is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control group not found")

        point = await self.point_service.get_last_id(body.id_template, session)
        point = PointBase(id=point)

        if body.is_clone_from_last:
            point = await self.get_last_point_in_group(body.id_control_group, session)

        for _ in range(body.number_of_points):
            new_point = PointControlEntity(**point.dict(exclude={"id",
                                                                 "register_value", }))
            new_point.name = f"Point {control_group.name} {_ + point.id + 1}"
            new_point.id_pointkey = f"Point{control_group.namekey}{_ + point.id + 1}".replace(" ", "")
            new_point.register = point.register_value
            new_point.id_control_group = body.id_control_group
            new_point.id_template = body.id_template
            session.add(new_point)

        await session.commit()
        return await self.get_template_detail(body.id_template, session)

    @async_db_request_handler
    async def get_last_point_in_group(self, id_control_group: int, session: AsyncSession):
        query = (select(PointControlEntity)
                 .where(PointControlEntity.id_control_group == id_control_group)
                 .where(PointControlEntity.status == 1)
                 .order_by(PointControlEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        return PointBase(**jsonable_encoder(result.scalars().first()))

    # region Control Group
    @async_db_request_handler
    async def add_new_control_group(self, body: ControlGroupAddFilter, session: AsyncSession):
        query = (select(PointListControlGroup)
                 .where(PointListControlGroup.id_template == body.id_template)
                 .where(PointListControlGroup.namekey == body.name.replace(" ", "")))
        result = await session.execute(query)
        control_group = result.scalars().first()
        if control_group is not None:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Control group with the same name already exists")

        new_group = PointListControlGroup(**PointControl(**body.dict(exclude={"id_points"}))
                                          .dict(exclude_unset=True),
                                          namekey=body.name.replace(" ", ""),
                                          status=1)
        session.add(new_group)
        await session.flush()

        if body.id_points:
            for id_point in body.id_points:
                await self.add_existing_point_to_group(new_group.id,
                                                       session,
                                                       PointControlAddFilter(id_control_group=new_group.id,
                                                                             id_point=id_point))

        await session.commit()
        return await self.get_template_detail(new_group.id_template, session)

    @async_db_request_handler
    async def update_control_group(self,
                                   body: ControlGroupUpdateFilter,
                                   session: AsyncSession):
        query = (select(PointListControlGroup)
                 .where(PointListControlGroup.id == body.id))
        result = await session.execute(query)
        control_group = result.scalars().first()
        if control_group is None:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control group not found")

        if body.attributes > 0 and body.attributes != control_group.attributes:
            query = (select(PointControlEntity)
                     .where(PointControlEntity.id_template == body.id_template)
                     .where(PointControlEntity.id_control_group == body.id))
            result = await session.execute(query)
            points = result.scalars().all()

            if body.attributes + 1 < len(points):
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                     detail="The number of attributes is greater than the number of points in the "
                                            "control group. Please remove points or increase the number of attributes.")

        query = (update(PointListControlGroup)
                 .where(PointListControlGroup.id == body.id)
                 .values(body.dict(exclude_unset=True, exclude={"id", "id_template"})))
        await session.execute(query)
        await session.commit()
        return await self.get_template_detail(control_group.id_template, session)

    @async_db_request_handler
    async def delete_control_group(self,
                                   body: ControlGroupDeleteFilter,
                                   session: AsyncSession):
        if len(body.id_group) == 0:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No control group to delete")

        for id_group in body.id_group:
            query = (select(PointListControlGroup)
                     .where(PointListControlGroup.id == id_group))
            result = await session.execute(query)
            control_group = result.scalars().first()
            if control_group is None:
                return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Control group not found")

            query = (select(PointControlEntity)
                     .where(PointControlEntity.id_template == body.id_template)
                     .where(PointControlEntity.id_control_group == id_group))
            result = await session.execute(query)
            points = result.scalars().all()
            for point in points:
                if point.id in body.id_points:
                    query = (delete(PointControlEntity)
                             .where(PointControlEntity.id == point.id))
                else:
                    query = (update(PointControlEntity)
                             .where(PointControlEntity.id == point.id)
                             .values(id_control_group=None))
                await session.execute(query)

            query = (delete(PointListControlGroup)
                     .where(PointListControlGroup.id == id_group))
            await session.execute(query)

        await session.commit()
        return await self.get_template_detail(body.id_template, session)
    # endregion
