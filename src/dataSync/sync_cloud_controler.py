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
from configs.config import orm_provider as config
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from dataSync.sync_cloud_service import *
from dataLog.file.file_service import *
from deviceControl.serviceDeviceControl.siteinfor_service import *

async def start_mqtt_service():
    global IdChannel 
    sync_data_instance = SyncData()
    log_file_instance = LogFile()
    mqtt_handler_instance = MQTTHandler1(sync_data_instance)
    
    db_new = await config.get_db()
    project_setup_config = await ProjectSetup.get_project_setup_values()
    time_interval_log_device = await ProjectSetup.get_time_interval_logdevice()
    time_sync = await ProjectSetupService.select_time_sync_cloud(db_new)
    time_interval = sync_data_instance.get_cycle_sync(time_sync,time_interval_log_device)
    typeOfFile = await log_file_instance.get_type_of_file(IdChannel)
    if project_setup_config is not None and time_sync is not None:
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
        if time_sync in [0,23]:
            scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'cron', hour=time_sync,args=[IdChannel,typeOfFile])
        elif time_sync in [95,95,99]:
            scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', hours=time_interval,args=[IdChannel,typeOfFile])
        elif time_sync in [97,98]:
            scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', minutes=time_interval,args=[IdChannel,typeOfFile])
        scheduler.start()
        # Sud message
        tasks = []
        typeOfFile = 1
        tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(mqtt_service,time_sync,IdChannel,typeOfFile,project_setup_config["serial_number"]))
        await asyncio.gather(*tasks, return_exceptions=False)
    await asyncio.sleep(0.05)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
asyncio.run(start_mqtt_service())
