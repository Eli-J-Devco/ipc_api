import json
import uuid

from mqtt_service.mqtt import Publisher

from .model import MessageModel
from ..config import config


class PM2Service:
    def __init__(self):
        self.sender = Publisher(host=config.PM2_MQTT_HOST,
                                port=config.PM2_MQTT_PORT,
                                subscriptions=[config.PM2_MQTT_TOPIC],
                                username=config.PM2_MQTT_USERNAME,
                                password=config.PM2_MQTT_PASSWORD.encode("utf-8"),
                                client_id=f"publisher-{config.PM2_MQTT_CLIENT_ID}-{uuid.uuid4()}",
                                will_qos=config.PM2_MQTT_QOS,
                                will_retain=config.PM2_MQTT_RETAIN)

    async def send(self, message: MessageModel):
        await self.sender.start()
        self.sender.send(config.PM2_MQTT_TOPIC, json.dumps(message.dict(exclude_unset=True)).encode("ascii"))
        await self.sender.stop()

