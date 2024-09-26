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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .devices_entity import (DeviceGroup as DeviceGroupEntity, DeviceType as DeviceTypeEntity,
                             DeviceConnection as DeviceConnectionEntity,
                             DeviceConnectionType as DeviceConnectionTypeEntity, Devices, DeviceComponent,
                             DeviceTypeGroup as DeviceTypeGroupEntity)
from .devices_filter import AddDeviceGroupFilter, ComponentEntity
from .devices_model import DeviceGroupBase, DeviceType, DeviceConnection, DeviceConnectionInfo, \
    ValidationRequireComponent, DeviceTypeGroup, DeviceConfigOutput, DeviceConnectionType, DeviceGroup
from ..template.template_entity import Template


@Injectable
class UtilsService:
    @async_db_request_handler
    async def add_device_group(self, body: AddDeviceGroupFilter, session: AsyncSession) -> dict:
        """
        Add device group to database
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: str
        """
        device_type = await self.get_device_type_by_id(body.id_device_type, session)

        if not device_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        new_device_group = DeviceGroupEntity(name=body.name,
                                             id_device_type=body.id_device_type,
                                             type=1)
        session.add(new_device_group)
        await session.flush()

        if device_type.type == 1:
            new_template = Template(name="Default",
                                    id_device_group=new_device_group.id,
                                    type=0)
            session.add(new_template)
            await session.flush()
        await session.commit()
        return {
            "message": "Device group added successfully",
            "id": new_device_group.id
        }

    @async_db_request_handler
    async def get_device_group(self, session: AsyncSession) -> list[DeviceGroup]:
        """
        Get device group
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: list[DeviceGroup] | HTTPException
        """
        query = select(DeviceGroupEntity)
        result = await session.execute(query)
        return list(map(lambda x: DeviceGroup(**x.__dict__), result.scalars().all()))

    @async_db_request_handler
    async def get_device_group_by_id(self, id_device_group: int, session: AsyncSession) -> DeviceGroupBase | HTTPException:
        """
        Get device group by id
        """
        query = select(DeviceGroupEntity).filter(DeviceGroupEntity.id == id_device_group)
        result = await session.execute(query)
        device_group = result.scalars().first()

        if not device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device group not found")

        return DeviceGroupBase(**device_group.__dict__)

    @async_db_request_handler
    async def get_device_group_by_type(self, id_device_type: int,
                                       session: AsyncSession) -> Sequence[DeviceGroupBase] | HTTPException:
        """
        Get device group by device type
        :author: nhan.tran
        :date: 26-08-2024
        :param id_device_type:
        :param session:
        :return: Sequence[DeviceGroup] | HTTPException
        """
        query = select(DeviceGroupEntity).filter(DeviceGroupEntity.id_device_type == id_device_type)
        result = await session.execute(query)
        device_group = result.scalars().all()

        if not device_group:
            return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device group not found")

        return device_group

    @async_db_request_handler
    async def get_device_type_group(self, session: AsyncSession) -> Sequence[DeviceTypeGroup]:
        """
        Get device type group
        :author: nhan.tran
        :date: 25-05-2024
        :param session:
        :return: list[DeviceTypeGroup] | HTTPException
        """
        query = select(DeviceTypeGroupEntity)
        result = await session.execute(query)
        device_type_groups = list(map(lambda x: DeviceTypeGroup(**{**x.__dict__, "addition": json.loads(x.addition)
                                      if x.addition is not None else []}),
                                      result.scalars().all()))
        return device_type_groups

    @async_db_request_handler
    async def get_device_type(self, session: AsyncSession) -> Sequence[DeviceType]:
        """
        Get device type
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: list[DeviceTypeEntity] | HTTPException
        """

        def convert_str_to_dict(obj):
            obj.plug_point_count = json.loads(obj.plug_point_count) if obj.plug_point_count is not None else None
            return obj.__dict__

        query = select(DeviceTypeEntity)
        result = await session.execute(query)
        device_types = result.scalars().all()
        return list(map(lambda x: DeviceType(**convert_str_to_dict(x)), device_types))

    @async_db_request_handler
    async def get_device_type_by_id(self, id_device_type: int,
                                    session: AsyncSession) -> DeviceType | HTTPException:
        """
        Get device type by id
        :author: nhan.tran
        :date: 21-05-2024
        :param id_device_type:
        :param session:
        :return: DeviceType | HTTPException
        """
        query = select(DeviceTypeEntity).filter(DeviceTypeEntity.id == id_device_type)
        result = await session.execute(query)
        device_type = result.scalars().first()

        if not device_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        return DeviceType(**device_type.__dict__)

    @async_db_request_handler
    async def get_device_type_by_group(self, id_device_type_group: int,
                                       session: AsyncSession) -> Sequence[DeviceType] | HTTPException:
        """
        Get device type by device group
        :author: nhan.tran
        :date: 22-08-2024
        :param id_device_type_group:
        :param session:
        :return:
        """
        query = select(DeviceTypeEntity).filter(DeviceTypeEntity.group == id_device_type_group)
        result = await session.execute(query)
        device_type = result.scalars().all()

        if not device_type:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device type not found")

        return device_type

    @async_db_request_handler
    async def get_device_type_by_device_group(self, id_device_group: int, session: AsyncSession) -> int | None:
        """
        Get device type by device group
        :author: nhan.tran
        :date: 20-05-2024
        :param id_device_group:
        :param session:
        :return: int | None
        """
        query = select(DeviceGroupEntity.id_device_type).filter(DeviceGroupEntity.id == id_device_group)
        result = await session.execute(query)
        return result.scalars().first()

    @async_db_request_handler
    async def get_connection_types(self, session: AsyncSession) -> list[DeviceConnectionType]:
        """
        Get connection types
        :author: nhan.tran
        :date: 16-09-2024
        :param session:
        :return: list[DeviceConnectionType]
        """
        query = select(DeviceConnectionTypeEntity)
        result = await session.execute(query)
        return list(map(lambda x: DeviceConnectionType(**x.__dict__), result.scalars().all()))

    @async_db_request_handler
    async def get_connection_by_device_id(self, device_id: int,
                                          device_table: str, session: AsyncSession) -> DeviceConnectionInfo | None:
        """
        Get connection by device id
        :author: nhan.tran
        :date: 20-09-2024
        :param device_id:
        :param device_table:
        :param session:
        :return: DeviceConnectionInfo | None
        """
        query = (select(DeviceConnectionEntity)
                 .filter(DeviceConnectionEntity.device_list_id == device_id)
                 .filter(DeviceConnectionEntity.device_table == device_table))
        result = await session.execute(query)
        component = result.scalars().first()

        if not component:
            return

        component = DeviceConnectionInfo(**component.__dict__)
        component_entity = ComponentEntity.__getitem__(component.connect_device_table).value
        query = (select(component_entity)
                 .where(component_entity.id == component.connect_device_id))
        result = await session.execute(query)
        connection_name = result.scalars().first().name
        component.connection_name = connection_name

        return component

    @async_db_request_handler
    async def validate_require_component(self, device_id: int, session: AsyncSession) -> ValidationRequireComponent:
        """
        Validate require component
        :author: nhan.tran
        :date: 24-09-2024
        :param device_id:
        :param session:
        :return: ValidationRequireComponent
        """
        query = (select(Devices)
                 .filter(Devices.id == device_id))
        result = await session.execute(query)
        component = result.scalars().first()
        validation_result = ValidationRequireComponent(is_require=False)
        if not component:
            return validation_result

        parent = component.parent
        logging.error(f"Component parent {parent}")
        if not parent:
            return validation_result

        query = (select(Devices)
                 .filter(Devices.id == parent))
        result = await session.execute(query)
        parent_component = result.scalars().first()

        if not parent_component:
            return validation_result

        query = (select(DeviceTypeEntity)
                 .filter(DeviceTypeEntity.id == component.id_device_type))
        result = await session.execute(query)
        device_type = result.scalars().first()
        device_type_group = device_type.group

        validation_result.parent = parent_component.id
        validation_result.is_require = await self.is_component_require(parent_component.id_device_type,
                                                                       device_type_group, session)
        return validation_result

    @async_db_request_handler
    async def is_component_require(self, main_type: int, component_type_group: int, session: AsyncSession) -> bool:
        """
        Check component require
        :author: nhan.tran
        :date: 24-09-2024
        :param main_type:
        :param component_type_group:
        :param session:
        :return: bool
        """
        query = (select(DeviceComponent)
                 .filter(DeviceComponent.main_type == main_type)
                 .filter(DeviceComponent.group == component_type_group))
        result = await session.execute(query)
        component = result.scalars().first()

        if not component:
            return False

        return component.require

    @async_db_request_handler
    async def get_device_config_information(self, session: AsyncSession) -> DeviceConfigOutput:
        """
        Get device config information
        :author: nhan.tran
        :date: 25-09-2024
        :param session:
        :return: DeviceConfigOutput
        """
        with session.no_autoflush:
            device_type_groups = await self.get_device_type_group(session)
            device_types = await self.get_device_type(session)
            device_groups = await self.get_device_group(session)
            connections = await self.get_connection_types(session)
            return DeviceConfigOutput(device_type_groups=device_type_groups,
                                      device_types=device_types,
                                      device_groups=device_groups,
                                      connections=connections)
