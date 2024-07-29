# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
from uuid import uuid1

import mqttools

from async_db.wrapper import async_db_request_handler
from utils.mqttManager import gzip_decompress


class DeviceService:
    def __init__(self,
                    host="127.0.0.1",
                    port=1883,
                    topic="",
                    username="",
                    password="",
                    serial_number="",
                    topic_parent=""
                    # device_parent=None,
                    # id_device=None,
                    # device_name=None,
                    ):
        self.mqtt_host = host
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.mqtt_username = username
        self.mqtt_password = bytes(password, 'utf-8')
        self.serial_number = serial_number
        self.topic_parent = topic_parent
        # self.device_parent = device_parent
        # self.id_device = id_device
        # self.device_name = device_name
        self.client = mqttools.Client(host=self.mqtt_host, 
                            port=self.mqtt_port,
                            username= self.mqtt_username, 
                            password=self.mqtt_password,
                            subscriptions=["#"],
                            # client_id='mqttools-{}'.format(uuid1().node),
                            connect_delays=[1, 2, 4, 8]
                            )
    @async_db_request_handler
    async def handle_messages_mqtt(self,client):
        
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic=f'{self.serial_number}/{self.topic_parent}'
            # topic_parent="/Init/API/Requests"
            if message.topic==topic:
                # print(f'device_name: {device_parent}')
                result=gzip_decompress(message.message)
                payload=result['PAYLOAD']['parent']
                print(result)
                print(payload)
                # device_parent=payload
                # print(self.id_device)
                # global device_parent
                # device_parent=payload
                # self.device_parent=payload
                # self.device_name=payload
                
    @async_db_request_handler
    async def subscribe_device(self):
        print("mqtt -------------------------------")

        try:
            await  self.client.start()
            await self.handle_messages_mqtt(self.client)
            await self.client.stop()
        except Exception as err:
            print("Error create_dev_no_log: ", err)
        finally:
            print("hello")