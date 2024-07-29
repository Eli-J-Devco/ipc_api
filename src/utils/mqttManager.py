# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import base64
import json
import os
import sys

import paho.mqtt.publish as publish

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
import gzip
from uuid import uuid1

import mqttools
from mqttools import SessionResumeError

from configs.config import Config

# IPC/Init/API/Requests
# IPC/Init/API/Responses
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC 
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD

# Describe functions before writing code
# /**
# 	 * @description public data MQTT
# 	 * @author vnguyen
# 	 * @since 02-04-2024
# 	 * @param {data_send}
# 	 * @return data ()
# 	 */
def mqtt_public_common(host,port,topic,username,password,data_send):
    try:

        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")

class mqttService:
    def __init__(self, host: str, port:int,username: str,password: str,serial_number: str):
        self.host=host
        self.port=port
        self.username=username
        self.password=bytes(password, 'utf-8')
        self.serial_number=serial_number
        self.sender = mqttools.Client(host=self.host, 
                            port=self.port,
                            username= self.username, 
                            password=self.password,
                            client_id='mqttools-{}'.format(uuid1().node),
                            # session_expiry_interval=15,
                            connect_delays=[1, 2, 4, 8]
                            )
    async def send(self,topic_parent: str,
                        message:str, 
                        resume_session: bool = True):

        try:
            # await self.sender.stop()
            await self.sender.start()
            payload = json.dumps(message)
            self.sender.publish(mqttools.Message(
                f"{self.serial_number}/{topic_parent}", payload.encode("ascii")))
        except Exception as err:
            print(f"Error MQTT public: '{err}'")
            raise err
        finally:
            await self.sender.stop()
    async def sendZIP(self,topic_parent: str,
                        message, 
                        resume_session: bool = True):

        try:
            gzip_compress = gzip.compress(json.dumps(message).encode("ascii"), 9)
            payload=base64.b64encode(gzip_compress)
            await self.sender.start()
            self.sender.publish(mqttools.Message(
                f"{self.serial_number}/{topic_parent}", payload))
        except Exception as err:
            print(f"Error MQTT public: '{err}'")
            raise err
        finally:
            await self.sender.stop()
def mqtt_public_paho(host: str,port:int,topic: str,username: str,password: str,message):
    try:

        payload = json.dumps(message)
        publish.single(topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")        
def mqtt_public_paho_zip(host: str,port:int,topic: str,username: str,password: str,message):
    try:

        gzip_compress = gzip.compress(json.dumps(message).encode("ascii"), 9)
        payload=base64.b64encode(gzip_compress)
        publish.single(topic, payload=payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")         
def gzip_decompress(message):
    try:
        result_decode=base64.b64decode(message.decode('ascii'))
        result_decompress=gzip.decompress(result_decode)
        return json.loads(result_decompress)
    except Exception as err:
        print(f"decompress: '{err}'") 