import asyncio
import base64
import json
import logging
import os
import pathlib
import time
import uuid

from mqtt_service.model import MessageModel, Topic
from mqtt_service.mqtt import Subscriber, Publisher
from mqttools import SessionResumeError
from sqlalchemy import Double, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .async_db.src.async_db.config import OrmProvider
from .config import orm_provider as db_config, config
from .create_table_module.create_table_service import CreateTableService, TableColumn
from .delete_table_module.delete_table_service import DeleteTableService
from .devices_entity import ProjectSetup, Devices
from .devices_model import Action, DeviceModel, DeviceStatus, DeviceState
from .pm2_service.model import MessageModel as PM2MessageModel, PayloadModel, DeviceModel as PM2DeviceModel
from .pm2_service.pm2_service import PM2Service
from .update_table_module.update_table_service import UpdateTableService

logger = logging.getLogger(__name__)


class MQTTSubscriber(Subscriber):
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 will_qos: int = 0,
                 retry_publisher: Publisher = None,
                 dead_letter_publisher: Publisher = None,
                 session: AsyncSession = None,
                 db_config: OrmProvider = None,
                 serial_number: str = None,
                 **kwargs):

        super().__init__(host=host,
                         port=port,
                         client_id=client_id,
                         subscriptions=topic,
                         username=username,
                         password=password,
                         will_retain=will_retain,
                         will_qos=will_qos,
                         **kwargs)
        self.topic = topic
        self.serial_number = serial_number
        self.retry_publisher = retry_publisher
        self.dead_letter_publisher = dead_letter_publisher

        self.create_table_service = CreateTableService(db_config.Base.metadata)
        self.delete_table_service = DeleteTableService(db_config.Base.metadata)
        self.update_table_service = UpdateTableService(db_config.Base.metadata)
        self.pm2_service = PM2Service(serial_number=serial_number)
        self.session = session
        self.topic = topic
        self.action = {
            Action.CREATE.value: self.create_table,
            Action.UPDATE.value: self.update_table,
            Action.DELETE.value: self.delete_table
        }

    async def connect_broker(self, resume_session: bool = True):
        logger.info(f"Client {self.client_id} starting...")
        try:
            await self.start(resume_session=resume_session)
        except SessionResumeError:
            await self.start()

    async def disconnect_broker(self):
        logger.info(f"Client {self.client_id} stopping...")
        await self.stop()

    async def get_message(self):
        logger.info(f"Client {self.client_id} started...")
        logger.info(f"Waiting for message from {self.topic}")
        while True:
            msg = await self.messages.get()
            if msg is None:
                logger.info("Broker connection lost!")
                break

            logger.info(f"Received message from {msg}")
            if msg.message is None:
                logger.info(f"Received empty message from {msg.topic}")
                time.sleep(3)
                continue

            logger.info(f"Received message from {msg.topic}")
            await self.process_message(msg.message)

    async def process_message(self, message):
        try:
            logger.info(f"Processing message: {message}")
            decoded_message = json.loads(base64.b64decode(message).decode("ascii"))
            logger.info(f"Decoded message: {decoded_message}")
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            return

        try:
            data = MessageModel(**decoded_message)
            logger.info(f"Action: {data.message.get('type')}")
            logger.info(f"Data: {data.message}")

            await self.get_devices_info(data)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            data = MessageModel(**decoded_message)
            await self.handle_error(e, data, self.retry_publisher, self.dead_letter_publisher)

    async def get_devices_info(self, data: MessageModel):
        devices = data.message.get("devices")
        action_type = data.message.get("type")
        code = data.message.get("code")
        retry = data.metadata.retry
        meta_code = data.metadata.code

        if action_type == Action.SET_PROJECT_MODE.value:
            await self.set_project_mode()
            await self.session.commit()
            return

        try:
            all_devices = await self.create_table_service.get_devices(self.session)
            devices_info = []
            id_templates = {}
            for device in all_devices:
                if device.id in devices:
                    if action_type != Action.DELETE.value:
                        if device.id_template not in id_templates:
                            id_templates[device.id_template] = (await (self.create_table_service
                                                                       .get_points(device.id_template,
                                                                                   self.session)))
                        device.points = id_templates[device.id_template]
                    devices_info.append(device)

            if not devices_info:
                logger.error("No devices found")
                return

            logger.info("Processing devices")
            result = {}
            send_device = []
            for device in devices_info:
                result[device.id] = await self.action[action_type](device, retry, code, meta_code)
                if result == 200:
                    send_device.append(PM2DeviceModel(id=device.id,
                                                      name=device.name,
                                                      id_communication=device.communication.id if device.communication else None,
                                                      connect_type=device.communication.name if device.communication else None,
                                                      mode=0,
                                                      device_type_value=device.device_type.type, ))
                    if action_type == Action.CREATE.value:
                        await self.update_table_service.update_device_status(device.id,
                                                                             DeviceState.Success.value,
                                                                             self.session)

            await self.set_project_mode()
            if len(send_device) > 0:
                if action_type != Action.UPDATE.value:
                    pm2_msg = PM2MessageModel(CODE=code,
                                              PAYLOAD=PayloadModel(
                                                  id_communication=send_device[0].id_communication,
                                                  device=send_device,
                                                  delete_mode=2 if action_type == Action.DELETE.value else None))
                else:
                    pm2_msg = PM2MessageModel(CODE=code,
                                              PAYLOAD=PayloadModel(id=devices_info[0].id_template, ))
                await self.pm2_service.send(pm2_msg)
            await self.session.commit()
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            await self.session.rollback()
            raise e

    async def create_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            logger.info(f"Creating table for device: {device.table_name}")
            result = await self.create_table_service.create_table(device.table_name,
                                                                  list(map(lambda x: TableColumn(x.id_pointkey,
                                                                                                 Double),
                                                                           device.points)),
                                                                  self.session)
            if isinstance(result, Exception):
                raise result

            logger.info(f"Adding device mppt for device: {device.table_name}")
            result = await self.create_table_service.add_device_mppt(device, self.session)
            if isinstance(result, Exception):
                raise result

            logger.info(f"Adding device point map for device: {device.table_name}")
            result = await self.create_table_service.add_device_point_list_map(device, self.session)
            if isinstance(result, Exception):
                raise result

            return 200
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.CREATE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.CREATE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher)
            if retry == 0:
                await self.update_table_service.update_device_status(device.id,
                                                                     DeviceState.Error.value,
                                                                     self.session)

    async def update_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            logger.info(f"Updating table for device: {device.table_name}")
            result = await self.update_table_service.update_table(device,
                                                                  self.session)

            if isinstance(result, Exception):
                raise result
            logger.info(f"Updated device mppt for device: {device.table_name}")

            return 200
        except Exception as e:
            logger.error(f"Error updating table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.UPDATE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.UPDATE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher)

    async def delete_table(self, device: DeviceModel, retry: int, code: str, meta_code: str):
        try:
            if device.device_type.type == 0:
                logger.info(f"Deleting table for device: {device.table_name}")
                result = await self.delete_table_service.delete_table(device.table_name, self.session)
                if isinstance(result, Exception):
                    raise result

                logger.info(f"Deleting device mppt for device: {device.table_name}")
                result = await self.delete_table_service.delete_device_mppt(device, self.session)
                if isinstance(result, Exception):
                    raise result

                logger.info(f"Deleting device point list map for device: {device.table_name}")
                result = await self.delete_table_service.delete_device_point_list_map(device, self.session)
                if isinstance(result, Exception):
                    raise result

            logger.info(f"Deleting device")
            result = await self.delete_table_service.delete_device(device.id, self.session)
            if isinstance(result, Exception):
                raise result

            return 200
        except Exception as e:
            logger.error(f"Error deleting table: {e}")
            await self.handle_error(e,
                                    MessageModel(
                                        topic=Topic(target=f"{self.serial_number}/{Action.DELETE.value}",
                                                    failed=f"{self.serial_number}/{Action.DEAD_LETTER.value}"),
                                        message={"type": Action.DELETE.value,
                                                 "devices": [device.id],
                                                 "code": code},
                                        metadata={"retry": retry,
                                                  "code": meta_code}),
                                    self.retry_publisher,
                                    self.dead_letter_publisher)

    async def set_project_mode(self):
        logger.info("Setting project mode")
        query = select(Devices).where(Devices.inverter_type.is_not(None))
        devices = await self.session.execute(query)
        devices = devices.scalars().all()

        query = select(ProjectSetup)
        project = await self.session.execute(query)
        project = project.scalars().first()
        logger.info(f"Current project mode: {project.mode}")

        is_auto = False
        is_manual = False
        for device in devices:
            if is_manual and is_auto:
                break

            if not is_manual and device.mode == 0:
                is_manual = True
                continue

            if not is_auto and device.mode == 1:
                is_auto = True
                continue

        mode = 2
        if is_manual and is_auto:
            mode = 2
        elif is_manual:
            mode = 0
        elif is_auto:
            mode = 1
        logger.info(f"Setting project mode to {mode}")

        if mode != project.mode:
            query = update(ProjectSetup).where(ProjectSetup.id == project.id).values(mode=mode)
            await self.session.execute(query)
        logger.info("Project mode set")


async def reconector():
    serial_number = await get_serial_number()
    session = await db_config.get_db()
    re_publisher = Publisher(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        subscriptions=[f"{serial_number}/{Action.CREATE.value}"],
        client_id=f"publisher-{DeviceStatus.CREATING.name.lower()}-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD.encode("utf-8")
    )

    dead_letter_publisher = Publisher(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        subscriptions=[f"{serial_number}/{Action.DEAD_LETTER.value}"],
        client_id=f"publisher-{DeviceStatus.DEAD_LETTER.name.lower()}-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD.encode("utf-8")
    )
    subscriber = MQTTSubscriber(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        topic=[f"{serial_number}/{topic.value}" for topic in Action if topic != Action.DEAD_LETTER],
        client_id=f"sub-{DeviceStatus.CREATING.name.lower()}-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        retry_publisher=re_publisher,
        dead_letter_publisher=dead_letter_publisher,
        session=session,
        db_config=db_config,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD.encode("utf-8"),
        serial_number=serial_number
    )
    while True:
        try:
            await subscriber.connect_broker()
            await subscriber.get_message()
            await subscriber.disconnect_broker()
        except KeyboardInterrupt:
            await subscriber.session.close()
            await subscriber.retry_publisher.disconnect()
            await subscriber.dead_letter_publisher.disconnect()
            asyncio.get_running_loop().close()
            break


async def get_serial_number():
    session = await db_config.get_db()
    serial_number = await session.execute(select(ProjectSetup))
    await session.close()
    return serial_number.scalars().first().serial_number


def run_subscriber():
    asyncio.run(reconector())
