import asyncio
import logging
import time
from abc import abstractmethod
import mqttools as mqtt
from mqttools import Message


class MQTTWorker:
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 qos: int = 0):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.topic = topic
        self.qos = qos
        self.will_retain = will_retain
        self.client = mqtt.Client(host=self.host,
                                  port=self.port,
                                  client_id=self.client_id,
                                  username=self.username,
                                  password=self.password,
                                  will_retain=self.will_retain,
                                  will_qos=self.qos,
                                  response_timeout=60,
                                  subscriptions=[(topic, self.qos) for topic in self.topic])

    async def connect(self, resume_session=False):
        logging.info(f"Connecting to {self.host}:{self.port}")
        await self.client.start(resume_session=resume_session)

    async def disconnect(self):
        logging.info(f"Disconnecting from {self.host}:{self.port}")
        await self.client.stop()


class MQTTPublisher(MQTTWorker):
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 qos: int = 0):
        super().__init__(host, port, client_id, topic, username, password, will_retain, qos)
        self.client.on_publish = self.on_publish

    def on_publish(self, flags, payload):
        try:
            logging.info(f"Message published to {self.topic} with {payload}")
        except ValueError:
            pass

    def publish(self, message: bytes):
        logging.info(f"Publishing message to {self.topic} - {message}")
        self.client.publish(Message(topic=self.topic[0], message=message))


class MQTTSubscriber(MQTTWorker):
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 qos: int = 0):
        super().__init__(host, port, client_id, topic, username, password, will_retain, qos)

    async def on_message(self, topic, message, retain, response_topic):
        await self.client.messages.put((topic, message, retain, response_topic))

    async def get_message(self):
        while True:
            logging.info(f"Waiting for message from {self.topic}")
            topic, message, retain, response_topic = await self.client.messages.get()

            if message is None:
                logging.info(f"Received empty message from {topic}")
                time.sleep(3)
                continue

            logging.info(f"Received message from {topic}")
            self.process_message(message)

    @abstractmethod
    def process_message(self, message: Message):
        pass
