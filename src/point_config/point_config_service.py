import logging

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .point_config_filter import PointTypeNames, PointType
from .point_config_entity import PointclassType as PointclassTypeEntity, PointListType as PointListTypeEntity
from .point_config_model import PointConfigFull
from .point_control_group_config_service import PointControlGroupConfigService
from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_model import ConfigInformationShort
from ..project_setup.project_setup_service import ProjectSetupService
from ..utils.service_wrapper import ServiceWrapper


@Injectable
class PointConfigService(PointControlGroupConfigService):
    def __init__(self, project_setup_service: ProjectSetupService):
        self.project_setup_service = project_setup_service

    @async_db_request_handler
    async def get_point_type(self):
        names = PointTypeNames().dict().values()
        return [{
            "id": PointType().__getattribute__(name),
            "name": name
        } for name in names]

    @async_db_request_handler
    async def get_data_type(self, session: AsyncSession):
        return await (self.project_setup_service
                      .get_config_information_by_type(session,
                                                      ConfigInformationType().TYPE_DATATYPE))

    @async_db_request_handler
    async def get_unit(self, session: AsyncSession):
        return await (self.project_setup_service
                      .get_config_information_by_type(session,
                                                      ConfigInformationType().TYPE_UNIT))

    @async_db_request_handler
    async def get_byte_order(self, session: AsyncSession):
        return await (self.project_setup_service
                      .get_config_information_by_type(session,
                                                      ConfigInformationType().TYPE_BYTEORDER))

    @async_db_request_handler
    async def get_type_class(self, session: AsyncSession):
        query = (select(PointclassTypeEntity))
        result = await session.execute(query)
        return [ConfigInformationShort(**r.__dict__) for r in result.scalars().all()]

    @async_db_request_handler
    async def get_type_list(self, session: AsyncSession):
        query = (select(PointListTypeEntity))
        result = await session.execute(query)
        return [ConfigInformationShort(**r.__dict__) for r in result.scalars().all()]

    @async_db_request_handler
    async def get_type_point_type(self, session: AsyncSession):
        return await (self.project_setup_service
                      .get_config_information_by_type(session,
                                                      ConfigInformationType().TYPE_POINT))

    @async_db_request_handler
    async def get_all_config(self, session: AsyncSession):
        data_type = await self.get_data_type(session)
        byte_order = await self.get_byte_order(session)
        point_unit = await self.get_unit(session)
        point_type = await self.get_type_point_type(session)
        point_class = await self.get_type_class(session)
        point_list = await self.get_type_list(session)

        return PointConfigFull(
            data_type=data_type,
            byte_order=byte_order,
            point_unit=point_unit,
            type_point=point_type,
            type_point_list=point_list,
            type_class=point_class
        )