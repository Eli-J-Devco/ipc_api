import logging
import time
from abc import abstractmethod

import paho.mqtt.client as mqtt


class MQTTWorker:
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 client_id: str,
                 topic: str,
                 qos: int = 0):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.topic = topic
        self.qos = qos
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                                  client_id=client_id,)
        self.client.username_pw_set(username, password)

    def connect(self):
        logging.info(f"Connecting to {self.host}:{self.port}")
        self.client.user_data_set([])
        self.client.connect(self.host, self.port, 300)
        self.client.loop_start()

    def disconnect(self):
        logging.info(f"Disconnecting from {self.host}:{self.port}")
        self.client.loop_stop()
        self.client.disconnect()

    def __del__(self):
        self.disconnect()


class MQTTPublisher(MQTTWorker):
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 client_id: str,
                 topic: str,
                 qos: int = 0):
        super().__init__(host, port, username, password, client_id, topic, qos)
        self.client.on_publish = self.on_publish

    def on_publish(self, client, userdata, mid, reason_code, properties):
        try:
            logging.info(f"Message published to {self.topic} with mid {mid}")
        except ValueError:
            pass

    def publish(self, message):
        logging.info(f"Publishing message to {self.topic} - {message}")
        self.client.publish(self.topic, message, qos=self.qos)


class MQTTSubscriber(MQTTWorker):
    def __init__(self,
                 host: str,
                 port: int,
                 username: str,
                 password: str,
                 client_id: str,
                 topic: str,
                 qos: int = 0):
        super().__init__(host, port, username, password, client_id, topic, qos)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        self.client.on_unsubscribe = self.on_unsubscribe

    def on_connect(self, client, userdata, flags, reason_code, properties):
        logging.info("Connected with result code "+str(reason_code))
        logging.info(f"Subscribing to {self.topic} with qos {self.qos}")
        try:
            self.client.subscribe(self.topic, qos=self.qos)
        except ValueError:
            pass

    def on_message(self, client, userdata, message):
        logging.info(f"Received message from {message.topic}")
        self.process_message(message.payload, userdata)

    def on_subscribe(self, client, userdata, mid, reason_code_list, properties):
        logging.info(f"Subscribed to {self.topic}")

        if len(reason_code_list) == 0:
            logging.info(f"Broker granted the following QoS: {self.qos}")

        if reason_code_list[0].is_failure:
            logging.info(f"Broker rejected you subscription: {reason_code_list[0]}")
        else:
            logging.info(f"Broker granted the following QoS: {reason_code_list[0].value}")

    def on_unsubscribe(self, client, userdata, mid, reason_code_list, properties):
        logging.info(f"Unsubscribed from {self.topic}")
        self.disconnect()

    def subscribe(self):
        logging.info(f"Connecting to {self.host}:{self.port}")
        try:
            self.client.loop_forever(300)
        except KeyboardInterrupt:
            self.unsubscribe()
            self.disconnect()

    def unsubscribe(self):
        logging.info(f"Unsubscribing from {self.topic}")
        self.client.unsubscribe(self.topic)

    @abstractmethod
    def process_message(self, message, userdata):
        pass
