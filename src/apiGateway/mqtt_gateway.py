import asyncio
import base64
import json
import os
import pathlib
import sys
import time
import uuid

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from mqtt_service.model import MessageModel, Topic
from mqtt_service.mqtt import Publisher, Subscriber
from sqlalchemy import Double
from sqlalchemy.ext.asyncio import AsyncSession

from apiGateway.devices import devices_service
from apiGateway.project_setup import project_service
from apiGateway.rs485 import rs485_service
from apiGateway.template import template_service
from apiGateway.upload_channel import upload_channel_service
from async_db.config import OrmProvider
from async_db.wrapper import async_db_request_handler
from configs.config import Config
from configs.config import orm_provider as db_config


class apiGateway(Subscriber):
    dta=[]
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic:  list[str] =None,
                 username: str = None,
                 password: str = None,
                 will_retain: bool = False,
                 will_qos: int = 0,
                 retry_publisher: Publisher = None,
                 dead_letter_publisher: Publisher = None,
                 session: AsyncSession = None,
                 db_config: OrmProvider = None,
                 **kwargs):

        super().__init__(host=host,
                         port=port,
                         client_id=client_id,
                         subscriptions=topic,
                         username=username,
                         password=bytes(password, 'utf-8'),
                         will_retain=will_retain,
                         will_qos=will_qos,
                         **kwargs)
        # project_init=project_service.ProjectService()
        # project_init.project_inform()
        
        print(f'topic: {topic}')
        self.topic = topic
        self.session = session
    async def connect_broker(self):
        # logger.info(f"Client {self.client_id} starting...")
        project_init=project_service.ProjectService()
        result_project=await project_init.project_inform(self.session)
        serial_number=result_project["serial_number"]

        self.topic_handlers = {
        f'{serial_number}/Init/API':self.handle_topic,
        f'{serial_number}/Init/API/Requests':self.handle_topic1,
        f'{serial_number}/Devices':self.handle_devices,
        }
        print(f"Client {self.client_id} starting...")
        await self.start()

    async def disconnect_broker(self):
        # logger.info(f"Client {self.client_id} stopping...")
        print(f"Client {self.client_id} stopping...")
        await self.stop()
    async def handle_topic(self,message):
        print('handle_topic')
        print(message)
        pass

    async def handle_topic1(self,message):
        print('handle_topic1')
        print(message)
        pass

    async def handle_devices(self,message):
        print('handle_devices')
        pass

    async def process_message(self,topic, message):
        print('process_message')
        # if topic in self.topic_handlers:
        #     await self.topic_handlers[topic](message)
        for key in self.topic_handlers:
            if topic.startswith(key):
                await self.topic_handlers[key](message)
                break
    async def handle_devices(self,message):
            print('handle_devices')
            pass
    async def get_topic(self):
        # logger.info(f"Client {self.client_id} started...")
        # logger.info(f"Waiting for message from {self.topic}")
        print(f"Client {self.client_id} started...")
        print(f"Waiting for message from {self.topic}")
        while True:
            msg = await self.messages.get()
            print(f'Topic:   {msg.topic}')
            if msg is None:
                # logger.info("Broker connection lost!")
                print("Broker connection lost!")
                break

            # logger.info(f"Received message from {msg}")
            print(f"Received message from {msg}")
            if msg.message is None:
                # logger.info(f"Received empty message from {msg.topic}")
                print(f"Received empty message from {msg.topic}")
                time.sleep(3)
                continue

            # logger.info(f"Received message from {msg.topic}")
            print(f"Received message from {msg.topic}")
            # await self.process_message(msg.message)
            await self.process_message(msg.topic,msg.message)
    async def handle_device_pub(self):
        pass

async def reconector(subscriber: apiGateway):
    while True:
        try:
            await subscriber.connect_broker()
            await subscriber.get_topic()
            await subscriber.disconnect_broker()
            # await subscriber.handle_device_pub()
        except KeyboardInterrupt:
            await subscriber.session.close()
            
if __name__ == "__main__":

    session = asyncio.run(db_config.get_db())
    subscriber = apiGateway(
        host= Config.MQTT_BROKER,
        port=Config.MQTT_PORT,
        topic=['#'],
        username= Config.MQTT_USERNAME,
        password= Config.MQTT_PASSWORD,
        client_id=f"sub-{uuid.uuid4()}",
        session=session,
    )

    asyncio.run(reconector(subscriber))