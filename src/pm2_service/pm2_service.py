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
                                subscriptions=["#"],
                                username=config.MQTT_USERNAME,
                                password=config.MQTT_PASSWORD.encode("utf-8"),
                                client_id=f"publisher-{config.MQTT_CLIENT_ID}-{uuid.uuid4()}",
                                will_qos=config.MQTT_QOS,
                                will_retain=config.MQTT_RETAIN)
        self.serial_number = serial_number

    async def send(self, message: MessageModel, resume_session: bool = True):
        try:
            await self.sender.start(resume_session=resume_session)
        except SessionResumeError:
            await self.sender.start()
        finally:
            self.sender.send(f"{self.serial_number}/{config.MQTT_INITIALIZE_TOPIC}",
                             json.dumps(message.dict()).encode("ascii"))
            await self.sender.stop()

