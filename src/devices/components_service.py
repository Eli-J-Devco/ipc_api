# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging
from functools import reduce
from typing import Sequence

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from .devices_entity import DeviceComponent as DeviceComponentEntity, Devices as DevicesEntity, \
    DeviceConnection as DeviceConnectionEntity
from .devices_filter import DeviceComponentFilter, GetDeviceComponentFilter, SymbolicDevice, GetComponentAdditionBase, \
    ComponentCode, GetAvailableComponentsFilter, FilterRangeEnum
from .devices_model import DeviceComponentList, DeviceComponent, DeviceComponentBase, Component, ComponentGroup, \
    DeviceComponentAddition, DeviceConnectionType, \
    DeviceComponentChild, DeviceConnectionInfo, DeviceFull
from .devices_utils_service import UtilsService
from ..config import env_config
from ..point.point_entity import Point
from ..template.template_entity import Template
from ..utils.pagination_model import Pagination


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
        if validate_quantity["is_valid"] is False:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Quantity limit exceeded")

        count = 1
        for component in components:
            if component.id:
                if is_add and component.type == 0:
                    continue
                query = (update(DevicesEntity)
                         .where(DevicesEntity.id == component.id)
                         .values(parent=parent,
                                 plug_point=component.plug_point
                                 if component.plug_point is not None else None))
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
                                                    connect_device_table=component.addition,
                                                    type=component.id_connection_type)
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
                 .where(DeviceComponentEntity.main_type == device_type.main_type))
        with session.no_autoflush:
            result = await session.execute(query)
            groups = result.scalars().all()
            output = []
            for group in groups:
                group_dict = group.__dict__
                base_component = DeviceComponentBase(**group_dict,
                                                     connection=DeviceConnectionType(
                                                         **group.connection_type.__dict__
                                                         if group.connection_type is not None else {})
                                                     )
                components = await self.utils_service.get_device_type_by_group(base_component.group, session)
                components = list(map(lambda x: DeviceComponentChild(**x.__dict__,
                                                                     connection=DeviceConnectionType(
                                                                         **group.connection_type.__dict__
                                                                         if group.connection_type is not None else {})),
                                      components))
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
                                   components: list[DeviceComponentFilter],
                                   session: AsyncSession) -> bool:
        """
        Component validation
        :author: nhan.tran
        :date: 17-06-2024
        :param parent:
        :param components:
        :param session:
        :return: bool
        """
        query = (select(DeviceComponentEntity)
                 .where(DeviceComponentEntity.main_type == parent))
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
        query = select(DevicesEntity).where(DevicesEntity.id == device_id)
        result = await session.execute(query)
        device = result.scalars().first()

        id_device_type = device.id_device_type
        id_template = device.id_template

        group_component = await self.get_device_components_by_main_type(GetDeviceComponentFilter(
            main_type=id_device_type, ), session)

        query = select(DevicesEntity).where(DevicesEntity.parent == device_id)
        result = await session.execute(query)
        components = list(result.scalars().all())
        output = []

        for group in group_component:
            if group.addition is not None:
                addition_quantity = await self.get_addition_components(GetComponentAdditionBase(table=group.addition,
                                                                                                id_template=id_template),
                                                                       session)
                group.quantity = addition_quantity.count

            formatted_group = ComponentGroup(**group.dict(exclude={"components"}))
            device_type_components = list(map(lambda x: x.id, group.components))
            device_components = list(filter(lambda x: x.id_device_type in device_type_components
                                                      and x.plug_point == formatted_group.plug_point,
                                            components))
            formatted_device_components = []
            for component in device_components:
                connection = await self.utils_service.get_connection_by_device_id(component.id,
                                                                                  "device_list",
                                                                                  session)
                connection_type = DeviceConnectionType(**group.connection.dict()
                if group.connection is not None else {})
                if connection:
                    connection.connection_type = connection_type
                else:
                    connection = DeviceConnectionInfo(connection_type=connection_type)

                formatted_device_components.append(Component(**component.__dict__,
                                                             image=component.device_type.image,
                                                             device_type_name=component.device_type.name,
                                                             connection=connection))
            formatted_group.components = formatted_device_components
            output.append(formatted_group)

        return output

    @async_db_request_handler
    async def get_device_component(self, main_type: int, group: int,
                                   plug_point: int, session: AsyncSession) -> DeviceComponentEntity:
        """
        Get device component by main type, group and plug point
        :author: nhan.tran
        :date: 04-10-2024
        :param main_type:
        :param group:
        :param plug_point:
        :param session:
        :return: DeviceComponent
        """
        query = (select(DeviceComponentEntity)
                 .where(DeviceComponentEntity.main_type == main_type)
                 .where(DeviceComponentEntity.group == group)
                 .where(DeviceComponentEntity.plug_point == plug_point))
        result = await session.execute(query)
        component = result.scalars().first()
        return component

    @async_db_request_handler
    async def validate_quantity(self, parent: int,
                                new_components: list[DeviceComponentFilter],
                                session: AsyncSession) -> dict | HTTPException:
        """
        Validate quantity
        :author: nhan.tran
        :date: 04-07-2024
        :param parent:
        :param new_components:
        :param session:
        :return: dict
        """
        # Cases:
        # 1. Actual components must be less than or equal to the limit for each plug point
        #    - Get all components by parent and group by plug point
        #    - Get quantity limit for each component
        # 2. Each component must follow the quantity limit
        # query = (select(DevicesEntity.plug_point, DevicesEntity.id_device_type, func.count())
        #          .where(DevicesEntity.parent == parent)
        #          .group_by(DevicesEntity.plug_point, DevicesEntity.id_device_type))
        # result = await session.execute(query)
        # components = result.all()

        def reduce_to_plug_point(acc, x):
            logging.error(f"{acc} acc")
            if not acc:
                x.append(1)
                return [x]

            for i in range(len(acc)):
                if acc[i][0] == x[0] and acc[i][1] == x[1]:
                    acc[i][2] += 1
                    break
            else:
                x.append(1)
                acc.append(x)
            return acc

        query = (select(DevicesEntity)
                 .where(DevicesEntity.id == parent))
        result = await session.execute(query)
        device = result.scalars().first()

        components = list(map(lambda x: [x.plug_point, x.id_device_type], new_components))
        components = list(reduce(lambda x, y: reduce_to_plug_point(x, y), components, []))

        id_device_type = device.id_device_type
        id_template = device.id_template

        device_type = await self.utils_service.get_device_type_by_id(id_device_type, session)
        if isinstance(device_type, HTTPException):
            return device_type
        device_type_plug_point = device_type.plug_point_count

        output = {}
        component_groups = {}
        if components:
            for component in components:
                # [plug_point]_[main_type]_[group]
                key = f"{component[0]}_{id_device_type}_{component[1]}"
                if key not in component_groups:
                    group = await self.utils_service.get_device_type_by_id(component[1], session)
                    if isinstance(group, HTTPException):
                        return group
                    component_info = await self.get_device_component(id_device_type, group.group,
                                                                     component[0], session)
                    component_groups[key] = {
                        "addition": component_info.addition,
                        "quantity": component_info.quantity
                    }
                addition_table = component_groups[key]["addition"]
                if addition_table is not None:
                    addition_filter = GetComponentAdditionBase(table=addition_table, id_template=id_template)
                    addition_quantity = await self.get_addition_components(addition_filter,
                                                                           session)
                    new_quantity = component_groups[key]["quantity"] + addition_quantity.count \
                        if component_groups[key]["quantity"] is not None else addition_quantity.count
                    component_groups[key]["quantity"] = new_quantity

                if component[0] not in output:
                    output[component[0]] = {"limit": device_type_plug_point.get(str(component[0]), 0),
                                            "actual": {
                                                component[1]: {
                                                    "limit": component_groups[key]["quantity"],
                                                    "actual": component[2]
                                                }
                                            }}
                else:
                    output[component[0]]["actual"][component[1]] = {
                        "limit": component_groups[key]["quantity"],
                        "actual": component[2]
                    }

        is_valid = True
        for plug_point in output.values():
            actual_count = reduce(lambda x, y: x + y["actual"], plug_point["actual"].values(), 0)
            if actual_count > plug_point["limit"]:
                is_valid = False
                break

            for group in plug_point["actual"].values():
                if group["actual"] > group["limit"]:
                    is_valid = False
                    break

        return {"is_valid": is_valid, "detail": output}

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

        query = (select(DeviceComponentEntity.quantity)
                 .where(DeviceComponentEntity.main_type == main_type)
                 .where(DeviceComponentEntity.group == component))
        result = await session.execute(query)
        quantity = result.scalar()
        return quantity

    @async_db_request_handler
    async def get_addition_components(self, body: GetComponentAdditionBase, session: AsyncSession):
        """
        Get addition components
        :author: nhan.tran
        :date: 09-09-2024
        :param body: GetInverterComponentAddition
        :param session: AsyncSession
        :return: int
        """
        entity_code = ComponentCode.__getitem__(body.table).value
        query = (select(Point)
                 .where(Point.id_template == body.id_template)
                 .where(Point.id_config_information == entity_code))
        result = await session.execute(query)
        addition = result.scalars().all()

        return DeviceComponentAddition(count=len(addition))

    @async_db_request_handler
    async def get_available_components_by_filter(self, body: GetAvailableComponentsFilter,
                                                 session: AsyncSession,
                                                 pagination: Pagination = None,):
        """
        Get available components by filter
        :author: nhan.tran
        :date: 30-09-2024
        :param body: GetAvailableComponentsFilter
        :param pagination: Pagination
        :param session: AsyncSession
        :return: list[DeviceComponent]
        """
        query = (select(DevicesEntity)
                 .where(or_(DevicesEntity.parent.is_(None), DevicesEntity.parent == body.parent))
                 .where(DevicesEntity.id.notin_(body.exclude)))

        if body.name is not None:
            query = query.where(DevicesEntity.name.like(f"%{body.name}%"))

        if body.id_device_type is not None:
            if isinstance(body.id_device_type, int):
                body.id_device_type = [body.id_device_type]
            query = query.where(DevicesEntity.id_device_type.in_(body.id_device_type))

        if body.id_communication is not None:
            if isinstance(body.id_communication, int):
                body.id_communication = [body.id_communication]
            query = query.where(DevicesEntity.id_communication.in_(body.id_communication))

        if body.ip_address is not None and body.ip_address != "":
            body.ip_address = body.ip_address.replace("*", "")
            query = query.where(DevicesEntity.tcp_gateway_ip.startswith(f"{body.ip_address}%"))

        validation_range = ["rtu_bus_address", "tcp_gateway_port"]
        for key in validation_range:
            if getattr(body, key) is not None:
                key_min = getattr(FilterRangeEnum, key.upper()).value["range_from"]
                key_max = getattr(FilterRangeEnum, key.upper()).value["range_to"]

                if getattr(body, key).range_from is not None and getattr(body, key).range_from > key_min:
                    query = query.where(getattr(DevicesEntity, key) >= getattr(body, key).range_from)
                if getattr(body, key).range_to is not None and getattr(body, key).range_to < key_max:
                    query = query.where(getattr(DevicesEntity, key) <= getattr(body, key).range_to)

        if pagination:
            if pagination.page or pagination.limit:
                if not pagination.page or pagination.page < 0:
                    pagination.page = env_config.PAGINATION_PAGE

                if not pagination.limit or pagination.limit < 0:
                    pagination.limit = env_config.PAGINATION_LIMIT

                query = (query
                         .offset(pagination.page)
                         .limit(pagination.limit))
        result = await session.execute(query)
        components = result.scalars().all()
        return list(map(lambda x: DeviceFull(**x.__dict__), list(components)))
