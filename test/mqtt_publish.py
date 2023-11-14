import datetime
import json
import random
import time

import paho.mqtt.publish as publish

broker = 'test.mosquitto.org'
port = 1883
topic = "IPC@123"
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "admin"
while True:
    CreatedAt = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    data = {"Hz": 50,
            "CreatedAt": CreatedAt,
            }
    payload = json.dumps(data)
    print(f"send data to Server ---------------{CreatedAt}")
    # publish.single(topic, payload, hostname=broker,
    #                auth={'username': MQTT_USERNAME, 'password': MQTT_PASSWORD})
    publish.single(topic, payload, hostname="test.mosquitto.org",
                   retain=False, port=port)
    time.sleep(1)
