# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import select, delete

from .point_mppt_service import PointMpptService
from .point_mppt_entity import PointMppt as PointMpptEntity
from .point_mppt_model import PointMpptBase, PointString, PointMppt
from ..devices.devices_service import DevicesService
from ..point.point_filter import DeletePointFilter
from ..point.point_model import PointBase
from ..point_config.point_config_filter import PointType


@Injectable
class NormalPointMpptService(PointMpptService):
    @async_db_request_handler
    async def get_last_string_formatted(self, id_template: int, parent: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == parent)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .order_by(PointMpptEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        last_string = result.scalars().first()

        if not last_string:
            return None

        last_string = PointString(**last_string.__dict__,
                                  register_value=last_string.register,
                                  children=[])

        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == last_string.id)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        panels = result.scalars().all()

        last_string.children = [PointMpptBase(**panel.__dict__) for panel in panels]

        return last_string

    @async_db_request_handler
    async def get_last_panel_point(self, id_template: int, id_point_string: int, is_clone: bool, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_string)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(PointMpptEntity.status == 1)
                 .order_by(PointMpptEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        last_panel = result.scalars().first()

        if is_clone:
            return PointMpptBase(**jsonable_encoder(last_panel)) if last_panel else None

        if not last_panel:
            return PointMpptBase()

        return PointMpptBase(register=last_panel.register)

    @async_db_request_handler
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession):
        new_point_mppt = PointMpptEntity(
            **point_mppt.dict(exclude={"id", "children"}),
            id_template=id_template,
            register=point_mppt.register_value
        )
        session.add(new_point_mppt)
        await session.flush()
        return new_point_mppt.id

    @async_db_request_handler
    async def add_string_point(self, id_template: int,
                               point_string: PointString,
                               id_point_mppt: int,
                               session: AsyncSession) -> int:
        new_point_string = PointMpptEntity(
            **point_string.dict(exclude={"id", "children", "parent"}),
            id_template=id_template,
            parent=id_point_mppt,
            register=point_string.register_value
        )
        session.add(new_point_string)
        await session.flush()
        return new_point_string.id

    @async_db_request_handler
    async def add_panel_point(self, id_template: int,
                              point_panel: PointBase,
                              id_point_string: int,
                              session: AsyncSession):
        new_point_panel = PointMpptEntity(
            **point_panel.dict(exclude={"id", "parent", "children", "register_value"}),
            id_template=id_template,
            parent=id_point_string,
            register=point_panel.register_value
        )
        session.add(new_point_panel)
        await session.flush()
        return new_point_panel.id

    @async_db_request_handler
    async def get_mppt_point(self, id_template: int, session: AsyncSession) -> list[dict]:
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_POINT)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return jsonable_encoder(points)

    @async_db_request_handler
    async def get_mppt_config_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_mppt)
                 .filter((PointMpptEntity.id_config_information == PointType().MPPT_VOLTAGE) |
                         (PointMpptEntity.id_config_information == PointType().MPPT_CURRENT))
                 .where(PointMpptEntity.status == 1)
                 .order_by(PointMpptEntity.id_config_information.asc()))
        result = await session.execute(query)
        points = result.scalars().all()
        return jsonable_encoder(points)

    @async_db_request_handler
    async def get_string_point(self, id_template: int, id_point_mppt: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_mppt)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        points = result.scalars().all()
        return jsonable_encoder(points)

    @async_db_request_handler
    async def get_panel_point(self, id_template: int, id_point_string: int, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_string)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(PointMpptEntity.status == 1))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())

    @async_db_request_handler
    async def delete_point(self, session: AsyncSession, body: DeletePointFilter):
        delete_ids = body.id_points

        for id_point in body.id_points:
            query = (select(PointMpptEntity)
                     .where(PointMpptEntity.parent == id_point)
                     .where(PointMpptEntity.id_template == body.id_template))

            result = await session.execute(query)
            children = jsonable_encoder(result.scalars().all())

            if children:
                children = [PointMpptBase(**child) for child in children]
                delete_ids.extend([child.id for child in children if child.id not in delete_ids])
                for child in children:
                    query = (select(PointMpptEntity)
                             .where(PointMpptEntity.parent == child.id)
                             .where(PointMpptEntity.id_template == body.id_template))
                    result = await session.execute(query)
                    panels = result.scalars().all()

                    if panels:
                        delete_ids.extend([panel.id for panel in panels if panel.id not in delete_ids])

        query = (delete(PointMpptEntity)
                 .where(PointMpptEntity.id.in_(delete_ids)))
        await session.execute(query, execution_options={"synchronize_session": False})
        await session.commit()
        await DevicesService().update_device_points(body.id_template, session)
        return await self.get_mppt_point_formatted(body.id_template, session)

    @async_db_request_handler
    async def add_mppt_point_formatted(self,
                                       points: list[PointMppt],
                                       id_template: int,
                                       session: AsyncSession):
        for point in points:
            new_point = PointMpptEntity(**PointBase(**point.dict(exclude_unset=True))
                                        .dict(exclude={"id",
                                                       "children",
                                                       "register_value",
                                                       "id_template"}),
                                        id_template=id_template,
                                        register=point.register_value)
            session.add(new_point)
            await session.flush()

            if point.children:
                for string in point.children:
                    new_child = PointMpptEntity(**PointBase(**string.dict(exclude_unset=True))
                                                .dict(exclude={"id",
                                                               "parent",
                                                               "register_value",
                                                               "children",
                                                               "id_template"}),
                                                parent=new_point.id,
                                                id_template=id_template, )
                    session.add(new_child)
                    await session.flush()
                    if string.id_config_information != PointType().MPPT_STRING:
                        continue

                    if string.children:
                        for panel in string.children:
                            new_panel = PointMpptEntity(**PointBase(**panel.dict(exclude_unset=True))
                                                        .dict(exclude={"id",
                                                                       "parent",
                                                                       "register_value",
                                                                       "id_template", }),
                                                        parent=new_child.id,
                                                        id_template=id_template)
                            session.add(new_panel)
                            await session.flush()

        return True
