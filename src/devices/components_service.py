# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging
from typing import Sequence

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, text, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_entity import DeviceComponent as DeviceComponentEntity, Devices as DevicesEntity
from .devices_filter import DeviceComponentFilter, GetDeviceComponentFilter, SymbolicDevice
from .devices_model import DeviceComponentList, DeviceComponent, DeviceComponentBase, Component, DeviceGroup
from .devices_utils_service import UtilsService
from ..template.template_entity import Template


@Injectable
class ComponentsService:
    def __init__(self, utils_service: UtilsService):
        self.utils_service = utils_service

    @async_db_request_handler
    async def add_components_parent(self,
                                    parent: int,
                                    components: list[DeviceComponentFilter],
                                    session: AsyncSession) -> Sequence[SymbolicDevice]:
        """
        Add parent to components
        :author: nhan.tran
        :date: 17-06-2024
        :param parent:
        :param components:
        :param session:
        :return: Sequence[SymbolicDevice]
        """
        symbolic_devices = []
        query = update(DevicesEntity).where(DevicesEntity.parent == parent).values(parent=None)
        await session.execute(query)
        await session.flush()

        for component in components:
            if component.id:
                query = (update(DevicesEntity)
                         .where(DevicesEntity.id == component.id)
                         .values(parent=parent))
                await session.execute(query)
                continue

            query = (select(Template)
                     .where(Template.id_device_group == component.id_device_group))
            result = await session.execute(query)
            template = result.scalars().first()
            if not template:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

            new_component = DevicesEntity(name=component.name,
                                          parent=parent,
                                          id_device_type=component.id_device_type,
                                          id_template=template.id, )
            session.add(new_component)
            await session.flush()
            symbolic_devices.append(SymbolicDevice(id=new_component.id, name=new_component.name))
        return symbolic_devices

    @async_db_request_handler
    async def get_device_components_by_main_type(self,
                                                 device_type: GetDeviceComponentFilter,
                                                 session: AsyncSession) -> Sequence[DeviceComponent]:
        """
        Get device components by main type
        :author: nhan.tran
        :date: 17-06-2024
        :param device_type:
        :param session:
        :return: Sequence[DeviceComponent]
        """
        query = (select(DeviceComponentEntity)
                 .where(DeviceComponentEntity.main_type == device_type.main_type)
                 .where(
                    DeviceComponentEntity.sub_type == device_type.sub_type
                    if device_type.sub_type else text("1=1")))

        result = await session.execute(query)
        components = result.scalars().all()
        output = []
        for component in components:
            logging.info(f"Component: {component.__dict__}")
            base_component = DeviceComponentBase(**component.__dict__)
            output.append(DeviceComponent(**base_component.dict(exclude_unset=True),
                                          name=component.component_type.name,
                                          type=component.component_type.type))
        return output

    @async_db_request_handler
    async def get_all_device_type_components(self,
                                             session: AsyncSession) -> Sequence[DeviceComponentList]:
        """
        Get all device type components
        :author: nhan.tran
        :date: 17-06-2024
        :param session:
        :return: Sequence[DeviceComponentList]
        """
        device_types = await self.utils_service.get_device_type(session)

        output = []
        for device_type in device_types:
            device_component = await (self.get_device_components_by_main_type(GetDeviceComponentFilter(
                main_type=device_type.id, ),
                session))
            if not device_component:
                continue

            base_output = DeviceComponentList(device_type=device_type,
                                              component=device_component)
            output.append(base_output)

        return output

    @async_db_request_handler
    async def component_validation(self,
                                   parent: int,
                                   sub_type: int,
                                   components: list[DeviceComponentFilter],
                                   session: AsyncSession) -> bool:
        """
        Component validation
        :author: nhan.tran
        :date: 17-06-2024
        :param parent:
        :param sub_type:
        :param components:
        :param session:
        :return: bool
        """
        query = (select(DeviceComponentEntity)
                 .where(DeviceComponentEntity.main_type == parent)
                 .where(or_(DeviceComponentEntity.sub_type == sub_type, DeviceComponentEntity.sub_type.is_(None))))
        result = await session.execute(query)
        component_types = result.scalars().all()

        if not component_types:
            return False

        component_types = [component.component for component in component_types]
        for component in components:
            if component.id_device_type not in component_types:
                return False
        return True

    @async_db_request_handler
    async def get_all_device_components(self, device_id: int, session: AsyncSession) -> list[int]:
        """
        Get all device components
        :author: nhan.tran
        :date: 17-06-2024
        :param device_id:
        :param session:
        :return: list[int]
        """
        query = select(DevicesEntity).where(DevicesEntity.parent == device_id)
        result = await session.execute(query)
        components = result.scalars().all()

        output = []
        if not components:
            return output

        for component in components:
            output.append(component.id)
            output += await self.get_all_device_components(component.id, session)
        return output

    @async_db_request_handler
    async def get_device_components(self,
                                    device_id: int,
                                    session: AsyncSession) -> list[Component]:
        """
        Get device components
        :author: nhan.tran
        :date: 17-06-2024
        :param device_id:
        :param session:
        :return: list[Component]
        """
        query = select(DevicesEntity).where(DevicesEntity.parent == device_id)
        result = await session.execute(query)
        components = result.scalars().all()
        output = []

        for component in components:
            component = Component(**jsonable_encoder(component))
            if not component.template_library:
                output.append(component)
                continue
            device_group = DeviceGroup(**jsonable_encoder(await self.utils_service
                                                          .get_device_group_by_id(component.template_library
                                                                                  .id_device_group, session)))
            component.device_group = device_group
            output.append(component)
        return output
