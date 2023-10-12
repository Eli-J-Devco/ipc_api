import paho.mqtt.publish as publish
import random
import time
import datetime
import json
broker = 'test.mosquitto.org'
port = 1883
topic = "IPC"
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
                   retain=False, client_id="IPC", port=port)
    time.sleep(1)
