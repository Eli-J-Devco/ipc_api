import asyncio
import base64
import json
import logging
import time
from abc import abstractmethod
import mqttools as mqtt
from mqttools import Message

from .model import MessageModel

logger = logging.getLogger(__name__)


class MQTTWorker(mqtt.Client):
    pass


class MQTTPublisher(MQTTWorker):
    def on_publish(self, flags, payload):
        try:
            logger.info(f"Message published to {self._subscriptions} with {payload}")
        except ValueError:
            pass

    def send(self, topic: str, message: bytes):
        logger.info(f"Publishing message to {topic} - {message}")
        self.publish(Message(topic=topic, message=message))


class MQTTSubscriber(MQTTWorker):
    async def on_message(self, message: Message):
        await self._messages.put((message.topic,
                                  message.message,
                                  message.retain,
                                  message.response_topic))

    @staticmethod
    async def handle_error(error,
                           data: MessageModel,
                           retry_publisher: MQTTPublisher,
                           dead_letter_publisher: MQTTPublisher):
        retry = data.metadata.retry
        topic = data.topic
        data.error = str(error)
        if retry > 0:
            logging.info(f"Retrying message: {retry}")
            data.metadata.retry = retry - 1
            await retry_publisher.start()
            retry_publisher.send(topic.target, base64.b64encode(json.dumps(data.dict()).encode("ascii")))
            await retry_publisher.stop()
            return

        logging.error(f"Dead letter message: {retry}")
        await dead_letter_publisher.start()
        dead_letter_publisher.send(topic.failed,
                                   base64.b64encode(json.dumps(data.dict()).encode("ascii")))
        await dead_letter_publisher.stop()
