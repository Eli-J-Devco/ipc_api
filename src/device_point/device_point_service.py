# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

from fastapi import HTTPException, status
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .device_point_entity import DevicePointMap as DevicePointEntity
from .device_point_filter import PointActionFilter, AlarmValueUpdateFilter, PointUpdateFilter
from .device_point_model import DevicePoint, DevicePointOutput, EnableField, TemplatePoint, PointUnit
from ..devices.devices_entity import Devices
from ..point.point_entity import Point
from ..project_setup.project_setup_filter import ConfigInformationType
from ..project_setup.project_setup_service import ProjectSetupService
from ..template.template_entity import Template


@Injectable
class DevicePointService:

    @async_db_request_handler
    async def get_device_point(self, device_id: int, session: AsyncSession) -> DevicePointOutput | HTTPException:
        """
        Get device point by device id
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param session:
        :return: DevicePointOutput | HTTPException
        """
        query = select(Devices.id_template).where(Devices.id == device_id)
        result = await session.execute(query)
        id_template = result.scalars().first()

        # Check if device exists
        if not id_template:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device not found")

        query = select(Template.type).where(Template.id == id_template)
        result = await session.execute(query)
        template_type = result.scalars().first()

        query = select(DevicePointEntity).where(DevicePointEntity.id_device_list == device_id)
        result = await session.execute(query)
        points = result.scalars().all()

        output = []
        for point in points:
            id_config_information = point.point_list.__dict__.get("id_type_units")
            enable_edit = EnableField(
                name=point.point_list.__dict__.get("nameedit"),
                unit=point.point_list.__dict__.get("unitsedit"),
            )

            unit = PointUnit(id=0, name="None")
            if id_config_information:
                unit = await ProjectSetupService().get_config_information(session, id_config_information)
            output.append(DevicePoint(**point.__dict__, unit=PointUnit(**unit.__dict__), enable_edit=enable_edit))

        return DevicePointOutput(points=output,
                                 template=TemplatePoint(id=id_template, type=template_type), )

    @async_db_request_handler
    async def points_action(self, body: PointActionFilter, session: AsyncSession) -> DevicePointOutput | HTTPException:
        """
        Enable or disable points by id
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: DevicePointOutput | HTTPException
        """
        points = body.id_point
        id_device = body.id_device
        status = False if body.action.lower().strip() == "disable" else True
        query = (update(DevicePointEntity)
                 .where(DevicePointEntity.id.in_(points))
                 .values(status=status))
        await session.execute(query)

        if body.id_devices_to_config:
            for device_id in body.id_devices_to_config:
                for point_id in points:
                    await self.point_action_by_device(device_id, point_id, status, session)

        await session.commit()
        return await self.get_device_point(id_device, session)

    @async_db_request_handler
    async def point_action_by_device(self,
                                     device_id: int,
                                     point_id: int,
                                     status: bool,
                                     session: AsyncSession) -> None:
        """
        Enable or disable points by device id
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param point_id:
        :param status:
        :param session:
        """
        query = select(DevicePointEntity.id_point_list).where(DevicePointEntity.id == point_id)
        result = await session.execute(query)
        point_list = result.scalars().first()

        query = (update(DevicePointEntity)
                 .where(DevicePointEntity.id_device_list == device_id)
                 .where(DevicePointEntity.id_point_list == point_list)
                 .values(status=status))
        await session.execute(query)

    @async_db_request_handler
    async def update_alarm_values(self, body: AlarmValueUpdateFilter, session: AsyncSession) -> DevicePointOutput | HTTPException:
        """
        Update alarm values by id
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: DevicePointOutput | HTTPException
        """
        for value in body.values:
            query = (update(DevicePointEntity)
                     .where(DevicePointEntity.id_device_list == body.id_device)
                     .where(DevicePointEntity.id == value.id_point)
                     .values(low_alarm=value.low_alarm, high_alarm=value.high_alarm))
            await session.execute(query)
        await session.commit()
        return await self.get_device_point(body.id_device, session)

    @async_db_request_handler
    async def update_point_per_edit(self, body: PointUpdateFilter, session: AsyncSession) -> DevicePointOutput | HTTPException:
        """
        Update point by id and device id
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: DevicePointOutput | HTTPException
        """
        query = (select(DevicePointEntity.id)
                 .where(DevicePointEntity.id_device_list == body.id_device))
        result = await session.execute(query)
        point = result.scalars().first()

        if not point:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device not found")

        query = (select(Point.id)
                 .where(Point.id == body.id_point_list))
        result = await session.execute(query)
        point_list = result.scalars().first()

        if not point_list:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Point not found")

        is_unit = ProjectSetupService().validate_config_information(body.id_type_units,
                                                                    ConfigInformationType.TYPE_UNIT)
        if isinstance(is_unit, HTTPException):
            return is_unit

        query = (select(DevicePointEntity.id)
                 .where(DevicePointEntity.id == body.id)
                 .where(DevicePointEntity.id_device_list == body.id_device)
                 .where(DevicePointEntity.id_point_list == body.id_point_list))
        result = await session.execute(query)
        device_point = result.scalars().first()

        if not device_point:
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device point not found")

        query = (update(DevicePointEntity)
                 .where(DevicePointEntity.id == body.id)
                 .values(name=body.name))
        await session.execute(query)

        query = (update(Point)
                 .where(Point.id == body.id_point_list)
                 .values(id_type_units=body.id_type_units))
        await session.execute(query)
        await session.commit()
        return await self.get_device_point(body.id_device, session)

    @async_db_request_handler
    async def get_units(self, session: AsyncSession) -> list[PointUnit] | HTTPException:
        """
        Get units
        :param session:
        :return: list[PointUnit] | HTTPException
        """
        return await ProjectSetupService().get_config_information_by_type(session, ConfigInformationType.TYPE_UNIT)
