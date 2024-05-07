from .mqtt_service.core import MQTTPublisher


class Publisher(MQTTPublisher):
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

    def publish(self, message):
        super().publish(message)

