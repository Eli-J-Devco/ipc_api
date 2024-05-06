import asyncio
import base64
import json
import logging
import uuid

import requests

from sqlalchemy import Double

from .config import config
from .publisher import Publisher
from .create_devices_model import CreateDeviceModel, Action, DeviceModel, DeviceState, Point
from .create_table_module.create_table_module import CreateTableModule
from .create_table_module.config import orm_provider as db_config
from .create_table_module.create_table_service import CreateTableService, TableColumn
from .utils.password_hasher import AccountHasher

from ..mqtt_service.main import MQTTSubscriber, MQTTPublisher


class Subscriber(MQTTSubscriber):
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 client_id: str,
                 topic: str,
                 qos: int = 0,
                 retry_publisher: MQTTPublisher = None,
                 dead_letter_publisher: MQTTPublisher = None):
        super().__init__(host, port, username, password, client_id, topic, qos)
        self.retry_publisher = retry_publisher
        self.dead_letter_publisher = dead_letter_publisher

        self.retry_publisher.connect()
        self.dead_letter_publisher.connect()
        self.db = CreateTableModule(db_config=db_config)
        asyncio.run(self.db.set_up())

    def process_message(self, message, userdata):
        try:
            logging.info(f"Processing message: {message} - {self.client.user_data_get()}")
            decoded_message = base64.b64decode(message).decode("ascii")
            logging.info(f"Decoded message: {decoded_message}")
        except Exception as e:
            logging.error(f"Error decoding message: {e}")
            return

        try:
            data = CreateDeviceModel(**json.loads(decoded_message))
            logging.info(f"Action: {data.type}")
            logging.info(f"Data: {data.devices}")

            if data.type == Action.CREATE.value:
                self.create_table(data.devices)

        except Exception as e:
            logging.error(f"Error processing message: {e}")
            data = CreateDeviceModel(**json.loads(decoded_message))
            if data.metadata.retry > 0:
                data.metadata.retry -= 1
                logging.info(f"Retrying message: {data.metadata.retry}")
                self.retry_publisher.publish(base64.b64encode(json.dumps(data.dict()).encode("ascii")))
                return

            logging.error(f"Dead letter message: {data.metadata.retry}")
            self.dead_letter_publisher.publish(base64.b64encode(json.dumps(data.dict()).encode("ascii")))

    def create_table(self, devices: list[int]):
        try:
            username = config.SETUP_USERNAME
            password = config.SETUP_PASSWORD

            username = AccountHasher().encrypt(username.encode(), config.PASSWORD_SECRET_KEY.encode())
            password = AccountHasher().encrypt(password.encode(), config.PASSWORD_SECRET_KEY.encode())

            logging.info(f"Username: {username}")
            logging.info(f"Password: {password}")

            response = requests.post(config.SETUP_URL + config.SETUP_AUTH_ENDPOINT,
                                     data={
                                         "username": username,
                                         "password": password
                                     },
                                     headers={"Content-Type": "application/x-www-form-urlencoded"})

            token = response.json().get("access_token")
            logging.info(f"Token: {token}")

            response = requests.post(config.SETUP_URL + config.SETUP_DEVICES_ENDPOINT,
                                     headers={"Authorization": f"Bearer {token}"})

            all_devices = response.json()
            devices_info = []
            id_templates = {}
            for device in all_devices:
                if device.get("id") in devices:
                    adding_device = DeviceModel(**device)
                    if adding_device.id_template not in id_templates:
                        id_templates[adding_device.id_template] = (requests
                                                                   .post(config.SETUP_URL +
                                                                         config.SETUP_POINTS_ENDPOINT +
                                                                         f"?id_template={adding_device.id_template}",
                                                                         headers={
                                                                             "Authorization": f"Bearer {token}"
                                                                         })
                                                                   .json())
                    adding_device.points = list(map(lambda x: Point(**x), id_templates[adding_device.id_template]))
                    devices_info.append(adding_device)

            for device in devices_info:
                async def create_table():
                    db = await self.db.db_config.get_db()
                    create_table_service = CreateTableService(db)
                    await create_table_service.create_table(device.table_name,
                                                            list(map(lambda x: TableColumn(x.id_pointkey,
                                                                                           Double),
                                                                     device.points)))

                asyncio.run(create_table())

        except Exception as e:
            logging.error(f"Error creating table: {e}")
            raise e


if __name__ == "__main__":
    re_publisher = Publisher(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.CREATE.value}",
        client_id=f"publisher-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2
    )

    dead_letter_publisher = Publisher(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.DEAD_LETTER.value}",
        client_id=f"publisher-{DeviceState.DEAD_LETTER.name.lower()}-{uuid.uuid4()}",
        qos=2
    )
    subscriber = Subscriber(
        host="localhost",
        port=1883,
        username="",
        password="",
        topic=f"{Action.CREATE.value}",
        client_id=f"sub-{DeviceState.CREATING.name.lower()}-{uuid.uuid4()}",
        qos=2,
        retry_publisher=re_publisher,
        dead_letter_publisher=dead_letter_publisher
    )

    subscriber.connect()
    subscriber.subscribe()
