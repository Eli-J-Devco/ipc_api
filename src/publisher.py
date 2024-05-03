from ..mqtt_service.core import MQTTPublisher


class Publisher(MQTTPublisher):
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 client_id: str,
                 topic: str,
                 qos: int = 0):
        super().__init__(host, port, username, password, client_id, topic, qos)

    def publish(self, message):
        super().publish(message)

