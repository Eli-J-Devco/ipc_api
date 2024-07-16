import asyncio
import base64
import json
import logging
import time
import uuid

from mqtt_service.model import MessageModel
from mqtt_service.mqtt import Subscriber, Publisher
from mqttools import SessionResumeError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .async_db.src.async_db.config import OrmProvider
from .config import orm_provider as db_config, config
from .create_table_module.create_table_service import CreateTableService
from .delete_table_module.delete_table_service import DeleteTableService
from .devices_entity import ProjectSetup, Devices
from .devices_model import Action, DeviceStatus, ActionEnum
from .devices_service import DeviceService
from .pm2_service.pm2_service import PM2Service
from .update_table_module.update_table_service import UpdateTableService
from .utils.utils import decompress_data
from .utils_service import UtilsService

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
        self.device_service = DeviceService(session=session,
                                            create_table_service=self.create_table_service,
                                            update_table_service=self.update_table_service,
                                            delete_table_service=self.delete_table_service,
                                            retry_publisher=self.retry_publisher,
                                            dead_letter_publisher=self.dead_letter_publisher,
                                            serial_number=self.serial_number,
                                            handle_error=self.handle_error,
                                            pm2_service=self.pm2_service)
        self.utils_service = UtilsService(device_service=self.device_service,
                                          session=session)
        self.action = {
            ActionEnum.Default.name: self.device_service,
            ActionEnum.Utils.name: self.utils_service
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
            decoded_message = decompress_data(message)
            decoded_message = json.loads(decoded_message)
            logger.info(f"Decoded message: {decoded_message}")
        except Exception as e:
            logger.error(f"Error decoding message: {e}")
            return

        try:
            data = MessageModel(**decoded_message)
            logger.info(f"Action: {data.message.get('type')}")
            logger.info(f"Data: {data.message}")

            await self.action[data.message.get("action")].handler(data)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            data = MessageModel(**decoded_message)
            await self.handle_error(e, data, self.retry_publisher, self.dead_letter_publisher)


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
