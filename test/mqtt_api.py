import threading
from flask import Flask
import subprocess
import asyncio
import logging
import os
app1 = Flask(__name__)
app2 = Flask(__name__)

data = ""


@app1.route('/', methods=['POST'])
def index1():
    global data
    pid = 1
    # result = os.system(f'pm2 delete {pid}')
    result = os.system(f'pm2  prettylist')
    print(f'Result :{result}')
    return 'Hello World 1'+str(data)


@app2.route('/', methods=['POST'])
def index2():
    global data
    # global data
    # data = data+1
    return 'Hello World 2'+str(data)


def FlaskApp1():
    app1.run(host='127.0.0.1', port=5000, debug=False, threaded=True)


def FlaskApp2():
    app2.run(host='127.0.0.1', port=5001, debug=False, threaded=True)


def AppMQtt():
    import paho.mqtt.client as mqtt
    broker = 'test.mosquitto.org'
    port = 1883
    topic = "IPC"
    # MQTT_USERNAME = "admin"
    # MQTT_PASSWORD = "admin"
    # The callback function of connection

    def on_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe(topic)

    # The callback function for received message
    def on_message(client, userdata, msg):
        global data
        data = msg.payload
        print(msg.topic+" "+str(msg.payload))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    # client.connect(broker, 1883, 60)
    client.connect(broker, port)
    # client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.loop_forever()


if __name__ == '__main__':

    # Executing the Threads seperatly.
    t1 = threading.Thread(target=FlaskApp1)
    t2 = threading.Thread(target=FlaskApp2)
    t3 = threading.Thread(target=AppMQtt)

    t1.start()
    t2.start()
    t3.start()
