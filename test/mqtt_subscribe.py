# import paho.mqtt.subscribe as subscribe
# import paho.mqtt.client as mqtt

import asyncio
import json
import logging
import sys
import time

import asyncio_mqtt as aiomqtt

broker = 'test.mosquitto.org'
port = 1883
topic = "IPC"
MQTT_USERNAME = "nextwave"
MQTT_PASSWORD = "123654789"


# The callback function of connection

# def on_connect(client, userdata, flags, rc):
#     print(f"Connected with result code {rc}")
#     client.subscribe(topic)

# # The callback function for received message


# def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))


# client = mqtt.Client()
# client.on_connect = on_connect
# client.on_message = on_message
# client.connect(broker, 1883, 60)
# client.username_pw_set("admin", "Nguyentanvu90py@")
# client.loop_forever(timeout=1.0, max_packets=1, retry_first_connection=False)


# async def main():
#     # reconnect_interval = 5  # In seconds
#     # logger.info("Connecting to MQTT")
#     # while True:
#     try:
#         # async with aiomqtt.Client(hostname=broker, port=1883, username=MQTT_USERNAME, password=MQTT_PASSWORD, client_id="1234") as client:
#         async with aiomqtt.Client("192.168.80.161", username=MQTT_USERNAME, password=MQTT_PASSWORD) as client:
#             # async with aiomqtt.Client("test.mosquitto.org") as client:
#             print("Connection to MQTT open")
#             async with client.messages() as messages:
#                 # await client.subscribe("humidity/#")
#                 await client.subscribe(topic)
#                 async for message in messages:
#                     print(message.payload.decode())
#     except aiomqtt.MqttError as error:
#         print("Connection to MQTT closed: " + str(error))
#     except Exception:
#         print("Connection to MQTT closed")
#         # await asyncio.sleep(reconnect_interval)

# asyncio.set_event_loop_policy(
#     asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
# asyncio.run(main())

import mqttools

# MQTT_BROKER = '115.78.133.129' 
# MQTT_PORT = 1883

MQTT_BROKER = '192.168.1.103' 
MQTT_PORT = 1885

# Publish   -> IPC@device_name
# Subscribe -> IPC@device_name@control

MQTT_USERNAME = "nextwave"
MQTT_PASSWORD ="123654789"
async def subscriber():
    print(f'MQTT_BROKER: {MQTT_BROKER}')
    print(f'MQTT_PORT: {MQTT_PORT}')
    # print(f'MQTT_TOPIC: {MQTT_TOPIC}')
    print(f'MQTT_USERNAME: {MQTT_USERNAME}')
    print(f'MQTT_PASSWORD: {MQTT_PASSWORD}')
    client = mqttools.Client(host=MQTT_BROKER, 
                             port=MQTT_PORT
                            #  username= MQTT_USERNAME, 
                            #  password=bytes(MQTT_PASSWORD, 'utf-8')
                             )
    # client = mqttools.Client(host=MQTT_BROKER, 
    #                          port=MQTT_PORT
    #                         )
    Topic="python/mqtt/#"
    await client.start()
    await client.subscribe(Topic)

    while True:
        message = await client.messages.get()

        if message is None:
            print('Broker connection lost!')
            break

        print(f'Topic:   {message.topic}')
        print(f'Message: {message.message.decode()}')
        print()

asyncio.run(subscriber())
# async def publisher():
#     Topic="IPC@UNO-DM-3.3-TL-PLUS"
#     async with mqttools.Client(host=MQTT_BROKER, 
#                              port=MQTT_PORT,
#                              username= MQTT_USERNAME, 
#                              password=b'123654789') as client:
#         client.publish(mqttools.Message(Topic, b'bar'))

# asyncio.run(publisher())
