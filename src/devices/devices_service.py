# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import base64
import datetime
import json
import logging
import uuid
from typing import Sequence, Any

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from fastapi import HTTPException, status

from sqlalchemy import select, update, text, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from mqtt_service.mqtt import Publisher
from mqtt_service.model import MessageModel, Topic, MetaData

from .devices_filter import AddDevicesFilter, IncreaseMode, CodeEnum, GetDeviceFilter, UpdateDeviceFilter, \
    AddDeviceGroupFilter
from .devices_model import Devices, DeviceFull, Action, DeviceConfigOutput
from .devices_entity import (Devices as DevicesEntity,
                             DeviceType as DeviceTypeEntity,
                             DeviceGroup as DeviceGroupEntity, DeviceGroup, DeviceType, )
from ..device_point.device_point_entity import DevicePointMap as DevicePointMapEntity, DevicePointMap
from ..config import env_config
from ..project_setup.project_setup_service import ProjectSetupService
from ..utils.PaginationModel import Pagination
from ..utils.utils import generate_pagination_response


@Injectable
class DevicesService:
    def __init__(self):
        # Initialize MQTT publisher
        self.sender = Publisher(
            host=env_config.MQTT_BROKER,
            port=env_config.MQTT_PORT,
            subscriptions=["#"],
            username=env_config.MQTT_USERNAME,
            password=env_config.MQTT_PASSWORD.encode("utf-8"),
            client_id=f"publisher-creating-{uuid.uuid4()}",
            will_qos=2
        )

    @async_db_request_handler
    async def get_devices(self, session: AsyncSession,
                          pagination: Pagination = None) -> list[DeviceFull] | HTTPException:
        """
        Get all devices from database
        :author: nhan.tran
        :date: 20-05-2024
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        query = (select(DevicesEntity)
                 .where(DevicesEntity.status.__eq__(True)))
        if pagination:
            if not pagination.page or pagination.page < 0:
                pagination.page = env_config.PAGINATION_PAGE

            if not pagination.limit or pagination.limit < 0:
                pagination.limit = env_config.PAGINATION_LIMIT

            query = (select(DevicesEntity)
                     .where(DevicesEntity.status.__eq__(True))
                     .offset(pagination.page)
                     .limit(pagination.limit))

        result = await session.execute(query)
        devices = result.scalars().all()

        total_query = (select(DevicesEntity.id)
                       .where(DevicesEntity.status.__eq__(True)))
        total_result = await session.execute(total_query)
        total = len(total_result.scalars().all())

        output = []
        for device in devices:
            driver_type = device.communication.__dict__.get("name")
            device_type = device.device_type.__dict__.get("name")
            device = device.__dict__
            device["driver_type"] = driver_type
            device["device_type"] = device_type
            output.append(DeviceFull(**device))

        return generate_pagination_response(output,
                                            total,
                                            pagination.page,
                                            pagination.limit,
                                            "/devices/get/all/") if pagination else output

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
        devices = []
        logging.info(f"Rate power: {body.rated_power}")
        for _ in range(body.num_of_devices):
            new_devices = DevicesEntity(
                **DeviceFull(
                    **body.dict(exclude_unset=True, exclude={"rtu_bus_address", "tcp_gateway_port"}),
                    rtu_bus_address=body.rtu_bus_address + (_ if body.inc_mode == IncreaseMode.RTU else 0),
                    tcp_gateway_port=body.tcp_gateway_port + (_ if body.inc_mode == IncreaseMode.TCP else 0),
                    rated_power_custom=body.rated_power,
                ).dict(exclude_none=True)
            )
            session.add(new_devices)
            await session.flush()

            tg = datetime.datetime.now(datetime.timezone.utc).strftime(
                "%Y%m%d"
            )

            query = (update(DevicesEntity)
                     .where(DevicesEntity.id == new_devices.id)
                     .values(table_name=f"dev_{new_devices.id}",
                             view_table=f"dev_{new_devices.id}_{tg}"))

            await session.execute(query)
            devices.append(new_devices.id)
        await session.commit()

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        code = CodeEnum.CreateRS485Dev.name if body.id_communication < 3 else CodeEnum.CreateTCPDev.name
        creating_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=f"{serial_number}/{Action.CREATE.value}",
                        failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
            message={"type": Action.CREATE.value,
                     "code": code,
                     "devices": devices}
        )
        await self.sender.start()
        self.sender.send(f"{serial_number}/{Action.CREATE.value}",
                         base64.b64encode(json.dumps(creating_msg.dict()).encode("ascii")))
        await self.sender.stop()

        if not pagination:
            pagination = Pagination(page=env_config.PAGINATION_PAGE, limit=env_config.PAGINATION_LIMIT)
        return await self.get_devices(session, pagination)

    @async_db_request_handler
    async def delete_device(self, device_id: int | list[int],
                            session: AsyncSession,
                            pagination: Pagination = None) -> list[DeviceFull] | HTTPException:
        """
        Delete device from database and send message to MQTT broker
        :author: nhan.tran
        :date: 20-05-2024
        :param device_id:
        :param session:
        :param pagination:
        :return: list[DeviceFull] | HTTPException
        """
        if isinstance(device_id, int):
            device_id = [device_id]
        serial_number = await ProjectSetupService().get_project_serial_number(session)
        del_msg = MessageModel(
            metadata=MetaData(retry=3),
            topic=Topic(target=f"{serial_number}/{Action.DELETE.value}",
                        failed=f"{serial_number}/{Action.DEAD_LETTER.value}"),
            message={"type": Action.DELETE.value,
                     "code": CodeEnum.DeleteDev.name,
                     "devices": device_id}
        )
        await self.sender.start()
        self.sender.send(f"{serial_number}/{Action.DELETE.value}",
                         base64.b64encode(json.dumps(del_msg.dict()).encode("ascii")))
        await self.sender.stop()

        if not pagination:
            pagination = Pagination(page=env_config.PAGINATION_PAGE, limit=env_config.PAGINATION_LIMIT)
        return await self.get_devices(session, pagination)

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
        return await self.get_devices(session)

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
    async def update_device(self, body: UpdateDeviceFilter, session: AsyncSession) -> list[DeviceFull] | HTTPException:
        """
        Update device in database and send message to MQTT broker
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: list[DeviceFull] | HTTPException
        """
        inverter_shutdown = None
        if body.enable_poweroff:
            inverter_shutdown = body.inverter_shutdown.strftime("%Y-%m-%d %H:%M:%S")

        query = (update(DevicesEntity)
                 .where(DevicesEntity.id == body.id)
                 .values(**body.dict(exclude_unset=True,
                                     exclude={"inverter_shutdown"}),
                         inverter_shutdown=inverter_shutdown))
        await session.execute(query)
        await session.commit()

        serial_number = await ProjectSetupService().get_project_serial_number(session)
        update_msg = {
            "CODE": CodeEnum.UpdateDev.name,
            "PAYLOAD": {
                "id": body.id,
            }
        }
        await self.sender.start()
        self.sender.send(f"{serial_number}/{env_config.MQTT_INITIALIZE_TOPIC}",
                         json.dumps(update_msg).encode("ascii"))
        return await self.get_devices(session)

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
                     "devices": device_id}
        )
        await self.sender.start()
        self.sender.send(f"{serial_number}/{Action.UPDATE.value}",
                         base64.b64encode(json.dumps(update_msg.dict()).encode("ascii")))
        await self.sender.stop()
        return True

    @async_db_request_handler
    async def add_device_group(self, body: AddDeviceGroupFilter, session: AsyncSession) -> str:
        """
        Add device group to database
        :author: nhan.tran
        :date: 20-05-2024
        :param body:
        :param session:
        :return: str
        """
        new_device_group = DeviceGroupEntity(name=body.name,
                                             id_device_type=body.id_device_type,
                                             type=1)
        session.add(new_device_group)
        await session.commit()
        return "Device group added successfully"
