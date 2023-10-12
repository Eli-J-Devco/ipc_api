# < Receive data used to log data, realtime >
import random
import asyncio
import logging
from opcua import Server
from opcua.server.binary_server_asyncio import BinaryServer
from opcua.server.internal_server import InternalServer
from opcua.server.event_generator import EventGenerator
from opcua.common.node import Node
from opcua.common.subscription import Subscription
from opcua.common.manage_nodes import delete_nodes
from opcua.client.client import Client
from opcua.crypto import security_policies
from opcua.common.event_objects import BaseEvent
from opcua.common.shortcuts import Shortcuts
from opcua.common.xmlexporter import XmlExporter
from opcua.common.xmlimporter import XmlImporter
from opcua.common.ua_utils import get_nodes_of_namespace
# from asyncua import Server
# from asyncua.common.callback import CallbackType
from paho.mqtt import client as mqtt_client
import asyncio_mqtt as aiomqtt

broker = 'test.mosquitto.org'
port = 1883
topic = "IPC"
client_id = f'mqtt-{random.randint(0, 100)}'
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "admin"
dataOfDevice = ""

tasks = []


async def main_mqtt():
    try:
        # async with aiomqtt.Client(hostname=broker, port=1883, username=MQTT_USERNAME, password=MQTT_PASSWORD, client_id="1234") as client:
        async with aiomqtt.Client("test.mosquitto.org") as client:
            print("Connection to MQTT open")
            async with client.messages() as messages:

                await client.subscribe("IPC/#")
                print("---------- MQTT -------------------")
                # async for message in messages:
                #     print(message.payload.decode())
                # await client.subscribe("#")
                # await client.subscribe("humidity/#")
                async for message in messages:
                    if message.topic.matches("IPC/Task"):
                        print(
                            f"Received data to [IPC/Task] {message.payload.decode()}")
                        global dataOfDevice
                        dataOfDevice = message.payload.decode()

                    if message.topic.matches("IPC/222"):
                        print(f"[IPC/111] {message.payload.decode()}")
                    if message.topic.matches("IPC/333"):
                        print(f"[IPC/111] {message.payload.decode()}")

    except aiomqtt.MqttError as error:
        print("Connection to MQTT closed: " + str(error))
    except Exception:
        print("Connection to MQTT closed")


async def main_log():
    while True:
        print("---------- main_log -------------------")
        # for task in asyncio.all_tasks():
        #     print(task.get_name())
        print(f"main : 5")
        await asyncio.sleep(2)


async def main():
    tasks.append(asyncio.create_task(main_mqtt(), name='MQTT'))
    tasks.append(asyncio.create_task(main_log(), name='main_log'))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # asyncio.run(main())
    # Declare event loop
    loop = asyncio.get_event_loop()
    # Run the code until completing all task
    loop.run_until_complete(main())
    # Close the loop
    # loop.close()
