import asyncio
import base64
import json
import logging
import time
import uuid

from mqtt_service.model import MessageModel
from mqtt_service.mqtt import Subscriber, Publisher
from mqtt_service.utils import decompress_data, gzip_data
from mqttools import SessionResumeError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .async_db.src.async_db.wrapper import async_db_request_handler
from .config import config, orm_provider as db_config, PlugPointEnum
from .devices_entity import (ProjectSetup, Devices, DeviceMppt as DeviceMpptEntity,
                             DeviceMpptString as DeviceMpptStringEntity,
                             DevicePanel as DevicePanelEntity, DeviceConnection as DeviceConnectionEntity, )
from .devices_model import TopicEnum, PayloadModel, ActionEnum, SLDResponseModel, DeviceModel, \
    DeviceMppt, DeviceMpptString, DevicePanel, DeviceConnection, DeviceConnectionEntityEnum, DeviceConnectionEnum

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
                 publisher: Publisher = None,
                 dead_letter_publisher: Publisher = None,
                 session: AsyncSession = None,
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
        self.publisher = publisher
        self.dead_letter_publisher = dead_letter_publisher
        self.session = session
        self.devices = []
        self.points = {}
        self.connections = []
        self.action = {
            ActionEnum.GetSLD.name: self.get_sld
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
            logger.info(f"Message processed!")

    async def process_message(self, message):
        logger.info(f"Process message: {message}")
        try:
            logger.info(f"Processing message: {message}")
            decoded_message = decompress_data(message)
            decoded_message = json.loads(decoded_message)
            logger.info(f"Decoded message: {decoded_message}")
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            await self.handle_error(e,
                                    message,
                                    self.publisher,
                                    self.dead_letter_publisher)
            return

        try:
            message = MessageModel(**decoded_message)
            payload = PayloadModel(**message.message)
            await self.action[ActionEnum(payload.type).name](payload)
        except Exception as e:
            logger.error(f"Exception: {e}")
            await self.handle_error(e,
                                    message,
                                    self.publisher,
                                    self.dead_letter_publisher)

    @async_db_request_handler
    async def get_sld(self, message: PayloadModel):
        start_ = time.time()
        logger.info(f"Get SLD: {message}")
        query = select(Devices)
        result = await self.session.execute(query)
        self.devices = list(map(lambda x: DeviceModel(**x.__dict__), result.scalars().all()))

        for device_connection in DeviceConnectionEntityEnum:
            query = select(device_connection.value)
            result = await self.session.execute(query)
            self.points[device_connection.name] = list(map(lambda x: DeviceConnectionEnum
                                                           .__getitem__(device_connection.name).value(**x.__dict__),
                                                           result.scalars().all()))

        query = select(DeviceConnectionEntity)
        result = await self.session.execute(query)
        self.connections = list(map(lambda x: DeviceConnection(**x.__dict__), result.scalars().all()))

        devices = self.get_devices()

        try:
            await self.publisher.stop()
            await self.publisher.start()
            self.publisher.send(f"{self.serial_number}/{TopicEnum.GET.value}",
                                gzip_data(json.dumps(devices)))
        except Exception as e:
            logger.error(f"Error: {e}")
            raise e
        finally:
            await self.publisher.stop()
        process_ = time.time() - start_
        await self.session.commit()
        logger.info(f"Process time: {process_}")

    def get_connection(self, connection: DeviceConnection):
        point = list(filter(lambda x: x.id == connection.connect_device_id,
                            self.points[connection.connect_device_table]))[0]
        connections = list(filter(lambda x: x.device_list_id == connection.connect_device_id and
                                            x.device_table == connection.connect_device_table,
                                  self.connections))
        if connections:
            connect_devices = list(filter(lambda x: x is not None,
                                          map(lambda x: self.get_connection(
                                              DeviceConnection(device_list_id=connection.connect_device_id,
                                                               device_table=connection.connect_device_table,
                                                               connect_device_id=x.connect_device_id,
                                                               connect_device_table=x.connect_device_table,
                                                               type=x.type)),
                                              connections)))
            point.children = connect_devices
        return point

    def get_devices(self, parent: int = None):
        devices = filter(lambda x: x.parent == parent, self.devices)

        if not devices:
            return []

        output = []
        for device in devices:
            device = SLDResponseModel(**device.__dict__)
            device.children = self.get_devices(device.id)

            connections = list(filter(lambda x: x.device_list_id == device.id, self.connections))
            if connections:
                connect_devices = list(filter(lambda x: x is not None,
                                              map(lambda x: self.get_connection(x),
                                                  connections)))
                device.children.extend(connect_devices)

            output.append(device.dict())

        return output


async def reconector():
    serial_number = await get_serial_number()
    session = await db_config.get_db()

    publisher = Publisher(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        subscriptions=[f"{serial_number}/{TopicEnum.GET.value}"],
        client_id=f"publisher-SLD-GET-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD.encode("utf-8")
    )

    dead_letter_publisher = Publisher(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        subscriptions=[f"{serial_number}/{TopicEnum.DEAD_LETTER.value}"],
        client_id=f"publisher-SLD-DeadLetter-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD.encode("utf-8")
    )

    subscriber = MQTTSubscriber(
        host=config.MQTT_HOST,
        port=config.MQTT_PORT,
        topic=[f"{serial_number}/{TopicEnum.WRITE.value}"],
        client_id=f"sub-SLD-WRITE-{uuid.uuid4()}",
        will_qos=config.MQTT_QOS,
        will_retain=config.MQTT_RETAIN,
        publisher=publisher,
        dead_letter_publisher=dead_letter_publisher,
        session=session,
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
            await subscriber.publisher.disconnect()
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
