
import asyncio
import base64
import hashlib
import json
import os
import sys
import time

import schedule
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# key =b'yYGx967p94hCCUaeJnImSkNjYjXPgQ3yHCl3Qf3pFUc='
# f = Fernet(key)
# # --------------------
# print(f'key: {key.decode()}')
# encId=b'gAAAAABlglnup_tJ4yFt7GdoKdDedKGx3QXM8BOboApkp0GKFVquZX4TabosOuWj7DuUcdCofCXF2zCSR0mxO767sbvHqCJG_Q=='
# decMessage = f.decrypt(encId)
# print(decMessage.decode('utf-8'))
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import datetime
from test.config import *

from utils.libMySQL import *


def get_utc():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    # print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
      return -1
    result=path_os[0:int(index_os)+len(string_find)]
    # print("Path directory relative:", result)
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)

def task(id):
   print("Executing the script...")
   time_insert_dev = get_utc()
   print(time_insert_dev)
  #  value_insert = (time_insert_dev, id ) 
  #  MySQL_Insert_v2(f'dev_0000{str(id)}', 1 ,value_insert) 

import atexit
# # schedule.every(10).seconds.do(task, id=2)
# # schedule.every(10).seconds.do(task, id=3)
# # schedule.every(10).seconds.do(task, id=4)
# # schedule.every().minute.at(":05").do(task, id=2)
# # schedule.every(5).seconds.until("00:47").do(task, id=2)
# schedule.every(1).minute.at(":00").do(task, id=2)
# schedule.every(5).to(5).minutes.do(task, id=2) 
# while True:
#    schedule.run_pending()
# #    time.sleep(1)
import datetime
import os
import time
from datetime import datetime
from time import sleep

import mqttools
import paho.mqtt.publish as publish
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import (BackgroundScheduler,
                                               BlockingScheduler)
from apscheduler.triggers.cron import CronTrigger


async def bar1():
    MQTT_BROKER = "127.0.0.1"
    MQTT_PORT = 1883
    MQTT_TOPIC = "IPC"
    MQTT_USERNAME = "nextwave"
    MQTT_PASSWORD = "123654789"
    client = mqttools.Client(host=MQTT_BROKER, 
                                port=MQTT_PORT,
                                username= MQTT_USERNAME, 
                                password=bytes(MQTT_PASSWORD, 'utf-8'))
    await client.start()
    await client.subscribe(MQTT_TOPIC)
    while True:
        message = await client.messages.get()
        print('bar1: ----------------------------------------------------')
        print(f'{datetime.now()} Bar1')
        if message is None:
                print('Broker connection lost!')
                break
        print(f'Topic:   {message.topic}')
        result=json.loads(message.message.decode())
        print(f'Message: {result}')
        
        # await asyncio.sleep(5)
async def main():
    tasks = []
    tasks.append(asyncio.create_task(bar1()))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.create_task(main())
    # loop.run_forever()
    asyncio.run(main())