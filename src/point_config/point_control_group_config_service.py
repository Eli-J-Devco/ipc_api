# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Sequence

from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_entity import PointListControlGroup as PointControlGroupEntity, PointListControlGroup
from ..devices.devices_entity import DeviceGroup
from ..template.template_entity import Template


class PointControlGroupConfigService:
    @async_db_request_handler
    async def get_control_groups(self,
                                 session: AsyncSession,
                                 id_template: int | None = None) -> Sequence[PointListControlGroup]:
        """
        Get control groups
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: Sequence[PointListControlGroup]
        """
        query = (select(PointControlGroupEntity)
                 .where(PointControlGroupEntity.id_template == id_template)
                 .where(PointControlGroupEntity.status == 1))

        if id_template is None:
            query = (select(PointListControlGroup)
                     .where(PointListControlGroup.status == True))

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    @async_db_request_handler
    async def get_control_group_by_device_type(id_device_type: int,
                                               session: AsyncSession) -> Sequence[PointListControlGroup]:
        query = (select(PointListControlGroup)
                 .where(PointListControlGroup.id_template == Template.id)
                 .where(Template.id_device_group == DeviceGroup.id)
                 .where(DeviceGroup.id_device_type == id_device_type))

        result = await session.execute(query)
        return result.scalars().all()
