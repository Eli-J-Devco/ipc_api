# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .point_mppt_service import PointMpptService
from .point_mppt_entity import PointMppt, ManualPointMppt as ManualPointMpptEntity
from .point_mppt_model import PointMpptBase, PointString
from ..point_config.point_config_filter import PointType


@Injectable
class ManualPointMpptService(PointMpptService):

    @async_db_request_handler
    async def add_string_point(self, id_template: int, point_string: PointString, id_point_mppt: int,
                               session: AsyncSession) -> int:
        pass

    @async_db_request_handler
    async def add_panel_point(self, id_template: int, point_panel: PointMpptBase, id_point_string: int,
                              session: AsyncSession):
        pass

    @async_db_request_handler
    async def get_last_point(self, id_template: int, session: AsyncSession) -> PointMppt:
        pass

    @async_db_request_handler
    async def get_last_panel_point(self, id_template: int, id_point_string: int, is_clone: bool,
                                   session: AsyncSession) -> PointMpptBase:
        pass

    @async_db_request_handler
    async def get_last_string_formatted(self, id_template: int, parent: int, session: AsyncSession) -> PointString:
        pass

    @async_db_request_handler
    async def add_point_mppt(self, id_template: int, point_mppt: PointMppt, session: AsyncSession) -> int:
        pass

    @async_db_request_handler
    async def get_mppt_point(self, id_device_type: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_POINT))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())

    @async_db_request_handler
    async def get_mppt_config_point(self, id_device_type: int, id_point_mppt: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_mppt)
                 .filter((ManualPointMpptEntity.id_config_information == PointType().MPPT_VOLTAGE) |
                         (ManualPointMpptEntity.id_config_information == PointType().MPPT_CURRENT))
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())

    @async_db_request_handler
    async def get_string_point(self, id_device_type: int, id_point_mppt: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_mppt)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_STRING)
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())

    @async_db_request_handler
    async def get_panel_point(self, id_device_type: int, id_point_string: int, session: AsyncSession):
        query = (select(ManualPointMpptEntity)
                 .where(ManualPointMpptEntity.id_device_type == id_device_type)
                 .where(ManualPointMpptEntity.parent == id_point_string)
                 .where(ManualPointMpptEntity.id_config_information == PointType().MPPT_PANEL)
                 .where(ManualPointMpptEntity.status == 1))
        result = await session.execute(query)
        return jsonable_encoder(result.scalars().all())
