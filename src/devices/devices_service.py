# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import base64
import datetime
import json
import logging
import uuid
from typing import Sequence

from fastapi import HTTPException, status
from mqtt_service.model import MessageModel, Topic, MetaData
from mqtt_service.mqtt import Publisher
from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler
from sqlalchemy import select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from .components_service import ComponentsService
from .devices_entity import (Devices as DevicesEntity,
                             )
from .devices_filter import AddDevicesFilter, IncreaseMode, CodeEnum, GetDeviceFilter, UpdateDeviceFilter, \
    DeleteDeviceFilter, SymbolicDevice, ListDeviceFilter, ActionEnum
from .devices_model import Devices, DeviceFull, Action
from .devices_utils_service import UtilsService
from ..config import env_config
from ..device_point.device_point_entity import DevicePointMap as DevicePointMapEntity, DevicePointMap
from ..point.point_entity import Point as PointEntity
from ..point_config.point_config_filter import PointType
from ..project_setup.project_setup_service import ProjectSetupService
from ..utils.pagination_model import Pagination
from ..utils.service_wrapper import ServiceWrapper
from ..utils.utils import generate_pagination_response


@Injectable
class DevicesService:
    def __init__(self):
        self.publisher = None
        self.publisher_info = {
            "host": env_config.MQTT_BROKER,
            "port": env_config.MQTT_PORT,
            "username": env_config.MQTT_USERNAME,
            "password": env_config.MQTT_PASSWORD.encode("utf-8"),
            "client_id": f"publisher-creating-{uuid.uuid4()}",
            "will_qos": 2
        }
        self.utils_service = UtilsService()
        self.components_service = ComponentsService(utils_service=self.utils_service)

    @async_db_request_handler
    async def get_publisher_info(self, session: AsyncSession):
        """
        Set up publisher
        """
        if "subscriptions" not in self.publisher_info:
            serial_number = await ProjectSetupService().get_project_serial_number(session)
            self.publisher_info["subscriptions"] = [serial_number]

        return self.publisher_info

    @async_db_request_handler
    async def get_devices(self,
                          body: ListDeviceFilter,
                          session: AsyncSession,
                          pagination: Pagination = None) -> list[DeviceFull] | HTTPException:
        """
        Get all devices from database
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        query = (select(DevicesEntity)
                 .where(DevicesEntity.status.__eq__(True))
                 .where(DevicesEntity.parent == body.id))
        if pagination:
            if pagination.page or pagination.limit:
                if not pagination.page or pagination.page < 0:
                    pagination.page = env_config.PAGINATION_PAGE

                if not pagination.limit or pagination.limit < 0:
                    pagination.limit = env_config.PAGINATION_LIMIT

                query = (select(DevicesEntity)
                         .where(DevicesEntity.status.__eq__(True))
                         .where(DevicesEntity.parent.is_(None))
                         .offset(pagination.page)
                         .limit(pagination.limit))

        result = await session.execute(query)
        devices = result.scalars().all()

        total_query = (select(DevicesEntity.id)
                       .where(DevicesEntity.parent.is_(None))
                       .where(DevicesEntity.status.__eq__(True)))
        total_result = await session.execute(total_query)
        total = len(total_result.scalars().all())

        output = []
        for device in devices:
            driver_type = device.communication.__dict__.get("name") if device.communication is not None else None
            device_type = device.device_type
            device_type_name = device.device_type.__dict__.get("name") if device.device_type is not None else None

            query = (select(DevicesEntity)
                     .where(DevicesEntity.parent == device.id))
            result = await session.execute(query)
            components = result.scalars().all()
            device = device.__dict__

            if components:
                device["children"] = True
            device["driver_type"] = driver_type if device_type and device_type.__dict__.get("type") != 1 \
                else device_type_name
            device["device_type"] = device_type.__dict__ if device_type else None

            output.append(DeviceFull(**device))

        return generate_pagination_response(output,
                                            total,
                                            pagination.page,
                                            pagination.limit,
                                            "/devices/get/all/") \
            if pagination and (pagination.page or pagination.limit) \
            else output

    @async_db_request_handler
    async def get_device_by_condition(self, body: GetDeviceFilter,
                                      session: AsyncSession) -> list[Devices] | HTTPException:
        """
        Get devices by condition
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: list[Devices] | HTTPException
        """
        template_id = body.id_template
        device_id = body.id_device
        query = (select(DevicesEntity)
                 .where(DevicesEntity.status.__eq__(True))
                 .where(DevicesEntity.id_template.__eq__(template_id) if template_id else text("1=1"))
                 .where(DevicesEntity.id.__ne__(device_id) if device_id else text("1=1")))
        result = await session.execute(query)
        devices = result.scalars().all()
        return [Devices(**device.__dict__) for device in devices]

    @async_db_request_handler
    async def get_device_by_id(self, device_id: int, session: AsyncSession) -> Devices | HTTPException:
        """
        Get device by id
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param session:
        :return: Devices | HTTPException
        """
        query = select(DevicesEntity).filter(DevicesEntity.id == device_id)
        result = await session.execute(query)
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Devices not found")

        return Devices(**device.__dict__)

    @async_db_request_handler
    async def get_device_by_template(self, id_template: int, session: AsyncSession) -> list[Devices] | HTTPException:
        """
        Get devices by template
        :author: nhan.tran
        :date: 20-05-2024
        :param id_template:
        :param session:
        :return: list[Devices] | HTTPException
        """
        query = select(DevicesEntity).filter(DevicesEntity.id_template == id_template)
        result = await session.execute(query)
        devices = result.scalars().all()
        return [Devices(**device.__dict__) for device in devices]

    @async_db_request_handler
    async def add_devices(self, body: AddDevicesFilter,
                          session: AsyncSession,
                          pagination: Pagination = None) -> list[DeviceFull] | HTTPException:
        """
        Add devices to database and send message to MQTT broker
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        is_symbolic_device = False
        devices = []
        symbolic_devices = []
        if not body.is_retry:
            device_type = await self.utils_service.get_device_type_by_id(body.id_device_type, session)
            is_symbolic_device = device_type.type == 1
            rtu_bus_address = body.rtu_bus_address
            tcp_gateway_port = body.tcp_gateway_port

            if body.components:
                sub_type = body.inverter_type if body.inverter_type else body.meter_type if body.meter_type else None
                if not await self.components_service.component_validation(body.id_device_type, sub_type,
                                                                          body.components, session):
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid component")

            count = 0
            for _ in range(body.num_of_devices):
                if body.num_of_devices > 1 and not is_symbolic_device:
                    if body.inc_mode == IncreaseMode.RTU:
                        rtu_bus_address += 1
                    else:
                        tcp_gateway_port += 1

                new_devices = DevicesEntity(
                    **DeviceFull(
                        **body.dict(exclude_unset=True,
                                    exclude={"rtu_bus_address", "tcp_gateway_port", "id_communication", "name"}),
                        name=f"{body.name}{f' {count + 1}' if body.num_of_devices > 1 else ''}",
                        rtu_bus_address=rtu_bus_address,
                        tcp_gateway_port=tcp_gateway_port,
                        rated_power_custom=body.rated_power,
                        id_communication=body.id_communication if not is_symbolic_device else None
                    ).dict(exclude_none=True, exclude={"children"})
                )
                session.add(new_devices)
                await session.flush()

                if not is_symbolic_device:
                    count += 1
                    tg = datetime.datetime.now(datetime.timezone.utc).strftime(
                        "%Y%m%d"
                    )

                    query = (update(DevicesEntity)
                             .where(DevicesEntity.id == new_devices.id)
                             .values(table_name=f"dev_{new_devices.id}",
                                     view_table=f"dev_{new_devices.id}_{tg}"))

                    await session.execute(query)
                else:
                    symbolic_devices.append(SymbolicDevice(id=new_devices.id, name=new_devices.name))

                if body.components:
                    symbolic_devices += await self.components_service.add_components_parent(new_devices.id,
                                                                                            body.components, session)
                devices.append(new_devices.id)
            await session.commit()
        else:
            devices = body.devices
            query = (update(DevicesEntity)
                     .where(DevicesEntity.id.in_(devices))
                     .where(DevicesEntity.creation_state == 1)
                     .values(creation_state=-1))
            await session.execute(query)
            await session.commit()

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        if not is_symbolic_device:
            code = None
            action = ActionEnum.Utils.name
            if not body.is_retry:
                code = CodeEnum.CreateRS485Dev.name if body.id_communication < 3 else CodeEnum.CreateTCPDev.name
                action = ActionEnum.Default.name

            creating_msg = MessageModel(
                metadata=MetaData(retry=3,
                                  code=body.secret),
                topic=Topic(target=f"{serial_number}/{Action.CREATE.value}",
                            failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
                message={"type": Action.CREATE.value,
                         "code": code,
                         "devices": devices if not body.is_retry else body.devices,
                         "action": action}
            )
            await ServiceWrapper.publish_message(publisher=self.publisher,
                                                 topic=f"{serial_number}/{Action.CREATE.value}",
                                                 message=[creating_msg],
                                                 publisher_info=await self.get_publisher_info(session))

        if len(symbolic_devices) > 0:
            msg = {
                "CODE": "CreateNoLogDev",
                "PAYLOAD": {
                    "device": [device.dict() for device in symbolic_devices]
                }
            }
            await ServiceWrapper.publish_message(publisher=self.publisher,
                                                 topic=f"{serial_number}/{env_config.MQTT_INITIALIZE_TOPIC}",
                                                 message=[msg],
                                                 publisher_info=await self.get_publisher_info(session),
                                                 is_decode=False)

        if not pagination:
            pagination = Pagination(page=env_config.PAGINATION_PAGE, limit=env_config.PAGINATION_LIMIT)
        return await self.get_devices(ListDeviceFilter(), session, pagination)

    @async_db_request_handler
    async def delete_device(self, devices: DeleteDeviceFilter,
                            session: AsyncSession,
                            pagination: Pagination = None) -> list[DeviceFull] | HTTPException:
        """
        Delete device from database and send message to MQTT broker
        :author: nhan.tran
        :date: 20-05-2024
        :param devices:
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        if isinstance(devices.device_id, int):
            device_id = [devices.device_id]
        else:
            device_id = devices.device_id

        deleted_devices = []
        for i in device_id:
            if i in deleted_devices:
                continue

            device = await self.get_device_by_id(i, session)
            if device:
                deleted_devices.append(device.id)
                query = (update(DevicesEntity)
                         .where(DevicesEntity.parent == device.id)
                         .values(parent=None))
                await session.execute(query)

        if len(deleted_devices) > 0:
            serial_number = await ProjectSetupService().get_project_serial_number(session)
            del_msg = MessageModel(
                metadata=MetaData(retry=3,
                                  code=devices.secret),
                topic=Topic(target=f"{serial_number}/{Action.DELETE.value}",
                            failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
                message={"type": Action.DELETE.value,
                         "code": CodeEnum.DeleteDev.name,
                         "devices": deleted_devices,
                         "action": ActionEnum.Default.name}
            )
            await ServiceWrapper.publish_message(publisher=self.publisher,
                                                 topic=f"{serial_number}/{Action.DELETE.value}",
                                                 message=[del_msg],
                                                 publisher_info=await self.get_publisher_info(session))
        logging.info("Sent delete message to MQTT broker")
        if not pagination:
            pagination = Pagination(page=env_config.PAGINATION_PAGE, limit=env_config.PAGINATION_LIMIT)

        await session.commit()
        session.expire_all()
        logging.info("Delete device successfully")
        return await self.get_devices(ListDeviceFilter(), session, pagination)

    @async_db_request_handler
    async def deactivate_device(self, device_id: int | list[int],
                                session: AsyncSession) -> list[DeviceFull] | HTTPException:
        """
        Deactivate device from database
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param session:
        :return: list[DeviceFull] | HTTPException
        """
        if isinstance(device_id, int):
            device_id = [device_id]
        query = (update(DevicesEntity)
                 .where(DevicesEntity.id.in_(device_id))
                 .values(status=False))
        await session.execute(query)
        await session.commit()
        return await self.get_devices(ListDeviceFilter(), session)

    @async_db_request_handler
    async def get_device_points(self, device_id: int, session: AsyncSession) -> Sequence[DevicePointMap]:
        """
        Get device points by device id
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param session:
        :return: list[DevicePointMapEntity] | HTTPException
        """
        query = select(DevicePointMapEntity).filter(DevicePointMapEntity.id_device_list == device_id)
        result = await session.execute(query)
        points = result.scalars().all()

        return points

    @async_db_request_handler
    async def update_device(self,
                            body: UpdateDeviceFilter,
                            session: AsyncSession,
                            pagination: Pagination) -> list[DeviceFull] | HTTPException:
        """
        Update device in database and send message to MQTT broker
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        inverter_shutdown = None
        if body.enable_poweroff:
            try:
                inverter_shutdown = body.inverter_shutdown.strftime("%Y-%m-%d %H:%M:%S")
            except AttributeError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time of inverter shutdown")

        query = (select(DevicesEntity)
                 .where(DevicesEntity.id == body.id))
        result = await session.execute(query)
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

        if body.components:
            sub_type = device.inverter_type if device.inverter_type \
                else device.meter_type if device.meter_type else None
            if not await self.components_service.component_validation(device.id_device_type,
                                                                      sub_type,
                                                                      body.components, session):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid component")

        query = (update(DevicesEntity)
                 .where(DevicesEntity.id == body.id)
                 .values(**body.dict(exclude_unset=True,
                                     exclude_none=True,
                                     exclude={"inverter_shutdown", "components"}),
                         inverter_shutdown=inverter_shutdown))
        await session.execute(query)

        symbolic_devices = await self.components_service.add_components_parent(body.id, body.components, session)
        if isinstance(symbolic_devices, HTTPException):
            return symbolic_devices

        await session.commit()

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        init_msg = []
        if len(symbolic_devices) > 0:
            msg = {
                "CODE": "CreateNoLogDev",
                "PAYLOAD": {
                    "device": [device.dict() for device in symbolic_devices]
                }
            }
            init_msg.append(msg)

        update_msg = {
            "CODE": CodeEnum.UpdateDev.name,
            "PAYLOAD": {
                "id": body.id,
            }
        }
        init_msg.append(update_msg)

        await ServiceWrapper.publish_message(publisher=self.publisher,
                                             topic=f"{serial_number}/{env_config.MQTT_INITIALIZE_TOPIC}",
                                             message=init_msg,
                                             publisher_info=await self.get_publisher_info(session),
                                             is_decode=False)
        return await self.get_devices(ListDeviceFilter(), session, pagination)

    @async_db_request_handler
    async def update_device_points(self, template_id: int, session: AsyncSession) -> bool:
        """
        Update device points by template id
        :author: nhan.tran
        :date: 20-05-2024
        :param template_id:
        :param session:
        :return: bool
        """
        await self.set_point_alias(template_id, session)

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        query = (select(DevicesEntity)
                 .where(DevicesEntity.id_template == template_id))
        result = await session.execute(query)
        devices = result.scalars().all()
        device_id = [device.id for device in devices]

        update_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=f"{serial_number}/{Action.UPDATE.value}",
                        failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
            message={"type": Action.UPDATE.value,
                     "code": CodeEnum.UpdateTemplate.name,
                     "devices": device_id,
                     "action": ActionEnum.Default.name}
        )
        await ServiceWrapper.publish_message(publisher=self.publisher,
                                             topic=f"{serial_number}/{Action.UPDATE.value}",
                                             message=[update_msg],
                                             publisher_info=await self.get_publisher_info(session))
        return True

    @async_db_request_handler
    async def set_point_alias(self, id_template: int, session: AsyncSession):
        """
        Set point alias
        :author: nhan.tran
        :date: 19-06-2024
        :param id_template:
        :param session:
        :return:
        """

        @async_db_request_handler
        async def update_point_alias(point: PointEntity, count: int = 0):
            query = (update(PointEntity)
                     .where(PointEntity.id == point.id)
                     .values(alias=f"{count}"))
            await session.execute(query)
            count += 1
            return count

        query = (select(PointEntity)
                 .where(PointEntity.id_template == id_template))
        result = await session.execute(query)
        points = result.scalars().all()
        count = 0

        point_types = PointType()
        normal_points = [point for point in points
                         if point.id_config_information == point_types.POINT and point.id_control_group is None]
        mppt_points = [point for point in points
                       if point.id_config_information != point_types.POINT]
        control_points = [point for point in points
                          if point.id_control_group is not None]
        for point in normal_points:
            count = await update_point_alias(point, count)

        for point in mppt_points:
            count = await update_point_alias(point, count)

        for point in control_points:
            count = await update_point_alias(point, count)

        await session.commit()
