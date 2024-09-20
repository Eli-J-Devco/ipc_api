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
from sqlalchemy import select, text

from .devices_entity import (DeviceGroup as DeviceGroupEntity, DeviceType as DeviceTypeEntity,
                             DeviceConnection as DeviceConnectionEntity,
                             DeviceConnectionType as DeviceConnectionTypeEntity)
from .devices_filter import AddDeviceGroupFilter, ComponentEntity
from .devices_model import DeviceGroup, DeviceType, DeviceInputMap, DeviceConnection, DeviceConnectionInfo
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
    async def get_device_group(self, session: AsyncSession) -> Sequence[DeviceGroup]:
        """
        Get device group
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :return: list[DeviceGroupEntity] | HTTPException
        """
        query = select(DeviceGroupEntity)
        result = await session.execute(query)
        return result.scalars().all()

    @async_db_request_handler
    async def get_device_group_by_id(self, id_device_group: int, session: AsyncSession) -> DeviceGroup | HTTPException:
        """
        Get device group by id
        """
        query = select(DeviceGroupEntity).filter(DeviceGroupEntity.id == id_device_group)
        result = await session.execute(query)
        device_group = result.scalars().first()

        if not device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device group not found")

        return device_group

    @async_db_request_handler
    async def get_device_group_by_type(self, id_device_type: int,
                                       session: AsyncSession) -> Sequence[DeviceGroup] | HTTPException:
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

        return device_type

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

    # @async_db_request_handler
    # async def get_input_map(self, device_id: int, session: AsyncSession):
    #     """
    #     Get input map
    #     """
    #     query = select(DeviceConnectionEntity).filter(DeviceConnectionEntity.device_list_id == device_id)
    #     result = await session.execute(query)
    #     input_map = list(map(lambda x: DeviceConnection(**x.__dict__), result.scalars().all()))
    #
    #     output = []
    #     for item in input_map:
    #         table = item.connect_device_table
    #         value = item.connect_device_id
    #         query = text(f"SELECT {table}.id, {table}.name FROM {table} WHERE {table}.id = {value}")
    #         result = await session.execute(query)
    #         result = result.first()
    #         output.append(DeviceInputMap(id=result[0], name=result[1]))
    #
    #     return output

    @async_db_request_handler
    async def get_connection_types(self, session: AsyncSession) -> Sequence[DeviceConnection]:
        """
        Get connection types
        :author: nhan.tran
        :date: 16-09-2024
        :param session:
        :return: Sequence[DeviceConnection]
        """
        query = select(DeviceConnectionTypeEntity)
        result = await session.execute(query)
        return result.scalars().all()

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
