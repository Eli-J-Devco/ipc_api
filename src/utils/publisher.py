from .mqtt_service.core import MQTTPublisher


class Publisher:
    def __init__(self,
                 host: str,
                 port: int,
                 client_id: str,
                 topic: list[str],
                 username: str = None,
                 password: str = None,
                 will_retain: bool = True,
                 qos: int = 0):
        self.client = MQTTPublisher(host=host,
                                    port=port,
                                    client_id=client_id,
                                    subscriptions=topic,
                                    username=username,
                                    password=password,
                                    will_retain=will_retain,
                                    will_qos=qos)
