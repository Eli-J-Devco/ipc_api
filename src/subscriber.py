import asyncio
import base64
import json
import logging
import os
import pathlib
import time
import uuid

from sqlalchemy import Double

from ..logger.logger import setup_logging
from ..mqtt_service.model import MessageModel, Topic
from .create_devices_model import CreateDeviceModel, Action, DeviceModel, DeviceState
from .create_table_module.config import orm_provider as db_config
from .create_table_module.create_table_module import CreateTableModule
from .create_table_module.create_table_service import CreateTableService, TableColumn
from .publisher import Publisher
from ..mqtt_service.main import MQTTSubscriber

logger = setup_logging(file_name="subscriber",
                       log_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "log"))


class Subscriber:
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 qos: int = 0,
                 retry_publisher: Publisher = None,
                 dead_letter_publisher: Publisher = None,
                 db_config: CreateTableModule = None):

        self.topic = topic
        self.client = MQTTSubscriber(host=host,
                                     port=port,
                                     client_id=client_id,
                                     subscriptions=topic,
                                     username=username,
                                     password=password,
                                     will_retain=will_retain,
                                     will_qos=qos)
        self.retry_publisher = retry_publisher.client
        self.dead_letter_publisher = dead_letter_publisher.client

        self.db = db_config
        self.create_table_service = CreateTableService(self.db.db_config.Base.metadata)
        self.topic = topic
        self.action = {
            Action.CREATE.value: self.create_table,
            Action.DELETE.value: self.delete_table
        }

    async def connect_broker(self):
        await self.client.start()

    async def get_message(self):
        logger.info(f"Waiting for message from {self.topic}")
        while True:
            topic, message, retain, response_topic = await self.client.messages.get()

            if message is None:
                logger.info(f"Received empty message from {topic}")
                time.sleep(3)
                continue

            logger.info(f"Received message from {topic}")
            await self.process_message(message)

    async def process_message(self, message):
        try:
            logging.info(f"Processing message: {message}")
            decoded_message = json.loads(base64.b64decode(message).decode("ascii"))
            logging.info(f"Decoded message: {decoded_message}")
        except Exception as e:
            logging.error(f"Error decoding message: {e}")
            return

        try:
            data = MessageModel(**decoded_message)
            logging.info(f"Action: {data.message.get('type')}")
            logging.info(f"Data: {data.message}")

            await self.get_devices_info(data)

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            data = MessageModel(**decoded_message)
            await self.client.handle_error(e, data, self.retry_publisher, self.dead_letter_publisher)

    async def get_devices_info(self, data: MessageModel):
        devices = data.message.get("devices")
        action_type = data.message.get("type")
        retry = data.metadata.retry

        try:
            db = await self.db.db_config.get_db()
            all_devices = await self.create_table_service.get_devices(db)
            devices_info = []
            id_templates = {}
            for device in all_devices:
                if device.id in devices:
                    if device.id_template not in id_templates:
                        id_templates[device.id_template] = (await (self.create_table_service
                                                                   .get_points(device.id_template,
                                                                               db)))
                    device.points = id_templates[device.id_template]
                    devices_info.append(device)

            for device in devices_info:
                await self.action[action_type](device, retry)
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            raise e

    async def create_table(self, device: DeviceModel, retry: int):
        try:
            logging.info(f"Creating table for device: {device.table_name}")
            await self.create_table_service.create_table(device.table_name,
                                                         list(map(lambda x: TableColumn(x.id_pointkey,
                                                                                        Double),
                                                                  device.points)),
                                                         await self.db.db_config.get_db())
        except Exception as e:
            logging.error(f"Error creating table: {e}")
            await self.client.handle_error(e,
                                           MessageModel(
                                               topic=Topic(target=Action.CREATE.value, failed=Action.DEAD_LETTER.value),
                                               message={"type": Action.CREATE.value, "devices": [device.id]},
                                               metadata={"retry": retry}),
                                           self.retry_publisher,
                                           self.dead_letter_publisher)

    async def delete_table(self, device: DeviceModel, retry: int):
        try:
            logging.info(f"Deleting table for device: {device.table_name}")
            await self.create_table_service.delete_table(device.table_name, await self.db.db_config.get_db())
        except Exception as e:
            logging.error(f"Error deleting table: {e}")
            await self.client.handle_error(e,
                                           MessageModel(
                                               topic=Topic(target=Action.DELETE.value, failed=Action.DEAD_LETTER.value),
                                               message={"type": Action.DELETE.value, "devices": [device.id]},
                                               metadata={"retry": retry}),
                                           self.retry_publisher,
                                           self.dead_letter_publisher)


if __name__ == "__main__":
    re_publisher = Publisher(
        host="localhost",
        port=1883,
        topic=[Action.CREATE.value],
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2
    )

    dead_letter_publisher = Publisher(
        host="localhost",
        port=1883,
        topic=[Action.DEAD_LETTER.value],
        client_id=f"publisher-{DeviceState.DEAD_LETTER.name.lower()}-{uuid.uuid4()}",
        qos=2
    )
    db = CreateTableModule(db_config)
    subscriber = Subscriber(
        host="localhost",
        port=1883,
        topic=[topic.value for topic in Action if topic != Action.DEAD_LETTER],
        client_id=f"sub-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2,
        retry_publisher=re_publisher,
        dead_letter_publisher=dead_letter_publisher,
        db_config=db
    )

    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    new_loop.create_task(subscriber.connect_broker())
    new_loop.create_task(subscriber.get_message())
    new_loop.run_forever()
