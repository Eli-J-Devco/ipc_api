import logging

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .point_mppt_service import PointMpptService
from .point_mppt_entity import PointMppt as PointMpptEntity
from .point_mppt_model import PointMpptBase, PointString, PointMppt
from ..point_config.point_config_filter import PointType


@Injectable
class NormalPointMpptService(PointMpptService):
    @async_db_request_handler
    async def get_last_mppt_point(self, id_template: int, is_clone: bool, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_POINT)
                 .where(PointMpptEntity.status == 1)
                 .order_by(PointMpptEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        last_mppt = result.scalars().first()

        if is_clone:
            return PointMppt(**jsonable_encoder(last_mppt)) if last_mppt else PointMppt()

        if not last_mppt:
            return PointMppt(register_value=0,
                             children=[])

        return PointMppt(register_value=last_mppt.register,
                         children=[])

    @async_db_request_handler
    async def get_last_string_point(self, id_template: int, id_point_mppt: int, is_clone: bool, session: AsyncSession):
        query = (select(PointMpptEntity)
                 .where(PointMpptEntity.id_template == id_template)
                 .where(PointMpptEntity.parent == id_point_mppt)
                 .where(PointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .where(PointMpptEntity.status == 1)
                 .order_by(PointMpptEntity.id.desc())
                 .limit(1))
        result = await session.execute(query)
        last_string = result.scalars().first()

        if is_clone:
            return PointString(**jsonable_encoder(last_string)) if last_string else PointString()

        if not last_string:
            return PointString(register_value=0,
                               children=[])

        return PointString(register_value=last_string.register,
                           children=[])

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
            return PointMpptBase(**jsonable_encoder(last_panel)) if last_panel else PointMpptBase()

        if not last_panel:
            return PointMpptBase(register_value=0)

        return PointMpptBase(register_value=last_panel.register)

    @async_db_request_handler
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession):
        new_point_mppt = PointMpptEntity(
            **point_mppt.dict(exclude={"id", "children", "register_value"}),
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
            **point_string.dict(exclude={"id", "children", "register_value", "parent"}),
            id_template=id_template,
            parent=id_point_mppt,
            register=point_string.register_value
        )
        session.add(new_point_string)
        await session.flush()
        return new_point_string.id

    @async_db_request_handler
    async def add_panel_point(self, id_template: int,
                              point_panel: PointMpptBase,
                              id_point_string: int,
                              session: AsyncSession):
        new_point_panel = PointMpptEntity(
            **point_panel.dict(exclude={"id", "children", "register_value", "parent"}),
            id_template=id_template,
            parent=id_point_string,
            register=point_panel.register_value
        )
        session.add(new_point_panel)
        await session.flush()
        return new_point_panel.id

    @async_db_request_handler
    async def get_mppt_point(self, id_template: int, session: AsyncSession):
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
