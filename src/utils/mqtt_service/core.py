import logging

import mqttools as mqtt
from mqttools import Message

logger = logging.getLogger(__name__)


class MQTTWorker(mqtt.Client):
    pass
    # def __init__(self, host: str, port: int, client_id: str, topic: list[str], username: str = None,
    #              password: str = None, will_retain: bool = True, qos: int = 0, **kwargs):
    #     super().__init__(host=host,
    #                      port=port,
    #                      client_id=client_id,
    #                      will_retain=will_retain,
    #                      username=username,
    #                      password=password,
    #                      will_qos=qos,
    #                      subscriptions=[(topic, qos) for topic in topic],
    #                      **kwargs)
    #     self.topic = topic


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
