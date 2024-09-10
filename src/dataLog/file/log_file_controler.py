# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# ********************************************************

import asyncio
import os
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
arr = sys.argv # Id Channel
IdChannel = arr[1]
from configs.config import MQTTSettings, MQTTTopicSUD,FolderSetting
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from dataLog.file.file_service import *
from deviceControl.serviceDeviceControl.siteinfor_service import *

async def consume_mqtt_messages(mqtt_service, client,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile):
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            payload = MQTTService.gzip_decompress(mqtt_service, message.message)
            await log_file_instance.handle_mqtt_message(mqtt_service,payload,time_interval_log_device,IdChannel,Head_File_Log,typeOfFile)
    except Exception as err:
        print(f"Error consuming MQTT messages: '{err}'")

async def subscribe_to_mqtt_topics(mqtt_service,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile):
    try:
        client = mqttools.Client(
            host=mqtt_service.host,
            port=mqtt_service.port,
            username=mqtt_service.username,
            password=bytes(mqtt_service.password, 'utf-8'),
            subscriptions=mqtt_service.topics,
            connect_delays=[1, 2, 4, 8]
        )
        while True :
            await client.start()
            await consume_mqtt_messages(mqtt_service, client,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile)
            await client.stop()
    except Exception as err:
        print(f"Error subscribing to MQTT topics: '{err}'")

async def start_mqtt_service():
    global IdChannel 
    log_file_instance = LogFile()
    project_setup_config = await ProjectSetup.get_project_setup_values()
    time_interval_log_device = await ProjectSetup.get_time_interval_logdevice()
    typeOfFile = await log_file_instance.get_type_of_file(IdChannel)
    if project_setup_config is not None and time_interval_log_device is not None:
        folder_parametter = FolderSetting()
        mqtt_settings = MQTTSettings()
        mqtt_topics = MQTTTopicSUD()
        mqtt_service = MQTTService(
            host=mqtt_settings.MQTT_BROKER,
            port=mqtt_settings.MQTT_PORT,
            username=mqtt_settings.MQTT_USERNAME,
            password=mqtt_settings.MQTT_PASSWORD,
            serial_number=project_setup_config["serial_number"]
        )
        mqtt_service.set_topics(mqtt_topics.Devices_All,)
        # Cycle Insert Device
        scheduler = AsyncIOScheduler()
        scheduler.add_job(log_file_instance.create_file_log, 'cron', minute=f'*/{time_interval_log_device}',args=[folder_parametter.Path_File_Log,folder_parametter.Head_File_Log,IdChannel,typeOfFile])
        scheduler.add_job(log_file_instance.delete_data_table_synced, 'cron', hour=f'*/1',)
        scheduler.start()
        # Sud message
        tasks = []
        tasks.append(subscribe_to_mqtt_topics(mqtt_service,time_interval_log_device,log_file_instance,IdChannel,folder_parametter.Head_File_Log,typeOfFile))
        await asyncio.gather(*tasks, return_exceptions=False)
    await asyncio.sleep(0.05)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
asyncio.run(start_mqtt_service())
