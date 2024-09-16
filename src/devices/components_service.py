# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import logging
from typing import Sequence

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, text, update, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func

from .devices_entity import DeviceComponent as DeviceComponentEntity, Devices as DevicesEntity, DeviceConnection as DeviceConnectionEntity
from .devices_filter import DeviceComponentFilter, GetDeviceComponentFilter, SymbolicDevice, GetAvailableComponents, \
    GetComponentAdditionBase
from .devices_model import DeviceComponentList, DeviceComponent, DeviceComponentBase, Component, ComponentGroup, \
    DeviceUploadChannelMap, DeviceComponentAdditionMap, DeviceComponentAddition
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
                                    session: AsyncSession,
                                    is_add: bool = True) -> Sequence[SymbolicDevice] | HTTPException:
        """
        Add parent to components
        :author: nhan.tran
        :date: 17-06-2024
        :param parent:
        :param components:
        :param session:
        :param is_add:
        :return: Sequence[SymbolicDevice] | HTTPException
        """
        symbolic_devices = []
        query = update(DevicesEntity).where(DevicesEntity.parent == parent).values(parent=None)
        await session.execute(query)
        await session.flush()

        validate_quantity = await self.validate_quantity(parent, components, session)
        for v in validate_quantity.values():
            if not v["limit"]:
                continue

            if v["actual"] > v["limit"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Quantity limit exceeded")

        count = 1
        for component in components:
            if component.id:
                if is_add and component.type == 0:
                    continue
                query = (update(DevicesEntity)
                         .where(DevicesEntity.id == component.id)
                         .values(parent=parent))
                await session.execute(query)
                continue

            id_device_group = component.id_device_group
            if is_add:
                device_group = await self.utils_service.get_device_group_by_type(component.id_device_type, session)
                if isinstance(device_group, HTTPException):
                    return device_group
                id_device_group = device_group[0].id

            query = (select(Template)
                     .where(Template.id_device_group == id_device_group))
            result = await session.execute(query)
            template = result.scalars().first()
            if not template:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

            component_name = component.name
            if not component_name:
                device_type = await (self.utils_service
                                     .get_device_type_by_id(component.id_device_type, session))
                component_name = device_type.name

            new_component = DevicesEntity(name=component_name,
                                          parent=parent,
                                          id_device_type=component.id_device_type,
                                          id_template=template.id,
                                          plug_point=component.plug_point
                                          if component.plug_point is not None else None)

            session.add(new_component)
            await session.flush()

            if component.addition is not None:
                connection = DeviceConnectionEntity(device_list_id=new_component.id,
                                                    device_table="device_list",
                                                    connect_device_table=component.addition)
                session.add(connection)
                await session.flush()

            symbolic_devices.append(SymbolicDevice(id=new_component.id, name=new_component.name))
            count += 1
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
                 .where(DeviceComponentEntity.sub_type == device_type.sub_type
                        if device_type.sub_type else text("1=1")))
        with session.no_autoflush:
            result = await session.execute(query)
            groups = result.scalars().all()
            output = []
            for group in groups:
                base_component = DeviceComponentBase(**group.__dict__)
                components = await self.utils_service.get_device_type_by_group(base_component.group, session)
                output.append(DeviceComponent(**base_component.dict(exclude_unset=True),
                                              name=group.component_type.name,
                                              type=group.component_type.type,
                                              components=components))
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

        component_types = [component.group for component in component_types]
        for component in components:
            if component.group not in component_types:
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
                                    session: AsyncSession) -> list[ComponentGroup]:
        """
        Get device components
        :author: nhan.tran
        :date: 17-06-2024
        :param device_id:
        :param session:
        :return: list[ComponentGroup]
        """
        query = select(DevicesEntity.id_device_type).where(DevicesEntity.id == device_id)
        result = await session.execute(query)
        id_device_type = result.scalar()
        group_component = await self.get_device_components_by_main_type(GetDeviceComponentFilter(
            main_type=id_device_type, ), session)

        query = select(DevicesEntity).where(DevicesEntity.parent == device_id)
        result = await session.execute(query)
        components = list(result.scalars().all())
        output = []

        for group in group_component:
            formatted_group = ComponentGroup(**group.dict(exclude={"components"}))
            device_type_components = list(map(lambda x: x.id, group.components))
            device_components = list(
                map(lambda x: Component(**x.__dict__, image=x.device_type.image,
                                        device_type_name=x.device_type.name),
                    list(filter(lambda
                                x: x.id_device_type in device_type_components
                                and x.plug_point == formatted_group.plug_point,
                                components))))
            formatted_group.components = device_components
            output.append(formatted_group)

        return output

    @async_db_request_handler
    async def validate_quantity(self, parent: int, new_components: list[DeviceComponentFilter], session: AsyncSession):
        """
        Validate quantity
        :author: nhan.tran
        :date: 04-07-2024
        :param parent:
        :param new_components:
        :param session:
        :return: dict
        """
        query = (select(DevicesEntity.id_device_type, DeviceComponentEntity.quantity, func.count())
                 .join(DeviceComponentEntity, DevicesEntity.id_device_type == DeviceComponentEntity.group)
                 .where(DevicesEntity.parent == parent)
                 .group_by(DevicesEntity.id_device_type))
        result = await session.execute(query)
        components = result.all()

        output = {}
        if components:
            for component in components:
                logging.info(f"Component: {component}")
                output[component[0]] = {"limit": component[1],
                                        "actual": component[2]}

        for component in new_components:
            if component.id_device_type not in output:
                output[component.id_device_type] = {"limit": await self.get_quantity(parent,
                                                                                     component.id_device_type,
                                                                                     session),
                                                    "actual": 0}
            output[component.id_device_type]["actual"] += 1

        return output

    @async_db_request_handler
    async def get_quantity(self, device_id: int, component: int, session: AsyncSession) -> int:
        """
        Get quantity
        :author: nhan.tran
        :date: 04-07-2024
        :param device_id:
        :param component:
        :param session:
        :return: int
        """
        query = (select(DevicesEntity.id_device_type,
                        DevicesEntity.inverter_type,
                        DevicesEntity.meter_type)
                 .where(DevicesEntity.id == device_id))
        result = await session.execute(query)
        device = result.first()

        main_type = device[0]
        sub_type = device[1] if device[1] else device[2] if device[2] else None

        query = (select(DeviceComponentEntity.quantity)
                 .where(DeviceComponentEntity.main_type == main_type)
                 .where(DeviceComponentEntity.group == component)
                 .where(or_(DeviceComponentEntity.sub_type == sub_type if sub_type else text("1=1"),
                            DeviceComponentEntity.sub_type.is_(None))))
        result = await session.execute(query)
        quantity = result.scalar()
        return quantity

    @async_db_request_handler
    async def get_available_components(self, body: GetAvailableComponents, session: AsyncSession):
        """
        Get available components
        :author: nhan.tran
        :date: 30-08-2024
        :param body: GetAvailableComponents
        :param session: AsyncSession
        :return: list[DeviceComponent]
        """

        query = (select(DevicesEntity)
                 .where(DevicesEntity.id_device_type == body.id_device_type)
                 .where(or_(DevicesEntity.parent.is_(None), DevicesEntity.parent == body.parent))
                 .where(DevicesEntity.id.notin_(body.exclude))
                 .where(DevicesEntity.name.like(f"%{body.name}%")))
        result = await session.execute(query)
        components = result.scalars().all()

        return list(map(lambda x: DeviceUploadChannelMap(**x.__dict__), list(components)))

    # @async_db_request_handler
    # async def get_addition_components(self, body: GetComponentAdditionBase, session: AsyncSession):
    #     """
    #     Get addition components
    #     :author: nhan.tran
    #     :date: 09-09-2024
    #     :param body: GetInverterComponentAddition
    #     :param session: AsyncSession
    #     :return: int
    #     """
    #     query = (select(DeviceComponentAdditionMapEntity)
    #              .where(DeviceComponentAdditionMapEntity.id == body.id))
    #     result = await session.execute(query)
    #     addition = DeviceComponentAdditionMap(**result.scalar().__dict__)
    #
    #     criteria = addition.criteria
    #     extract_criteria = criteria.split(addition.extract_symbol)
    #     for c in extract_criteria:
    #         extract_each_criteria = c.split("=")
    #         try:
    #             logging.info(f"Extract each criteria: {extract_each_criteria[0].strip()}")
    #             if body.__getattribute__(extract_each_criteria[0].strip()) is not None:
    #                 criteria = (criteria
    #                             .replace(f"{extract_each_criteria[0]}=?",
    #                                      f"{extract_each_criteria[0]}={str(body.__getattribute__(extract_each_criteria[0].strip()))}"))
    #         except AttributeError:
    #             continue
    #     target = addition.target
    #
    #     query = text(f"SELECT COUNT(*) FROM {target} WHERE {criteria}")
    #     result = await session.execute(query)
    #
    #     return DeviceComponentAddition(count=result.scalar(), addition=json.loads(addition.addition_column))
