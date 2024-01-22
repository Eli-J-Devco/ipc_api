# import asyncio
# import json
# import time
# # from controllers import bar, foo
# from datetime import datetime

# import mqttools
# import paho.mqtt.publish as publish
# from apscheduler.schedulers.asyncio import AsyncIOScheduler


# def func_mqtt_public(host, port,topic, username, password, data_send):
#     try:
#         print(f'public data to MQTT')
#         payload = json.dumps(data_send)
#         publish.single(topic, payload, hostname=host,
#                     retain=False, port=port,
#                     auth = {'username':f'{username}', 
#                             'password':f'{password}'})

#     except Exception as err:
#         print(f"Error MQTT public: '{err}'")
# async def foo(value):
#     print(f'foo: ---------------------------------------------------- {value}')
#     print(f'{datetime.now()} Foo')

# data=0

# async def bar():
#     # while True:
#         # print('bar2: ----------------------------------------------------')
#         global data
#         data +=1
#         # print(data)
#         # print(f'{datetime.now()} Bar2')
#         MQTT_BROKER = "127.0.0.1"
#         MQTT_PORT = 1883
#         MQTT_TOPIC = "IPC"
#         MQTT_USERNAME = "nextwave"
#         MQTT_PASSWORD = "123654789"
#         func_mqtt_public(MQTT_BROKER,MQTT_PORT,MQTT_TOPIC,MQTT_USERNAME,MQTT_PASSWORD,data)
#         # await asyncio.sleep(5)
# async def main():
#     # Init message
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(foo, 'cron', second="*/1",args=["111"])
#     scheduler.add_job(bar, 'cron', second="*/1",args=[])
#     # scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
#     # scheduler.add_job(foo, 'cron', minute="*/5",args=["111"])
#     scheduler.start()

# if __name__ == "__main__":
#     # loop = asyncio.get_event_loop()
#     # loop.create_task(main())
#     # loop.run_forever()
#     asyncio.get_event_loop().run_forever()


import logging
import os
import sys


def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from logger_manager import LoggerSetup

# setup root logger
logger_setup = LoggerSetup(path,"TEST")
LOGGER = logging.getLogger(__name__)
LOGGER.info("--- Running App ---")