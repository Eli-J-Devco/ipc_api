# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Sequence

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .devices_entity import DeviceGroup as DeviceGroupEntity, DeviceType as DeviceTypeEntity
from .devices_filter import AddDeviceGroupFilter
from .devices_model import DeviceGroup, DeviceType
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device group not found")

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
        query = select(DeviceTypeEntity)
        result = await session.execute(query)
        return result.scalars().all()

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
