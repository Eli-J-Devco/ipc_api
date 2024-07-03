import json
import uuid

from mqtt_service.mqtt import Publisher
from mqttools import SessionResumeError

from .model import MessageModel
from ..config import config


class PM2Service:
    def __init__(self, serial_number: str):
        self.sender = Publisher(host=config.MQTT_HOST,
                                port=config.MQTT_PORT,
                                subscriptions=[serial_number],
                                username=config.MQTT_USERNAME,
                                password=config.MQTT_PASSWORD.encode("utf-8"),
                                client_id=f"publisher-{config.MQTT_CLIENT_ID}-{uuid.uuid4()}",
                                will_qos=config.MQTT_QOS,
                                will_retain=config.MQTT_RETAIN,
                                connect_delays=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        self.serial_number = serial_number

    async def send(self, message: MessageModel):
        if not self.sender:
            self.sender = Publisher(host=config.MQTT_HOST,
                                    port=config.MQTT_PORT,
                                    subscriptions=[self.serial_number],
                                    username=config.MQTT_USERNAME,
                                    password=config.MQTT_PASSWORD.encode("utf-8"),
                                    client_id=f"publisher-{config.MQTT_CLIENT_ID}-{uuid.uuid4()}",
                                    will_qos=config.MQTT_QOS,
                                    will_retain=config.MQTT_RETAIN,
                                    connect_delays=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024])
        await self.sender.stop()
        try:
            await self.sender.start()
            self.sender.send(f"{self.serial_number}/{config.MQTT_INITIALIZE_TOPIC}",
                             json.dumps(message.dict()).encode("ascii"))
        except Exception as e:
            raise e
        finally:
            await self.sender.stop()

