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

from configs.config import MQTTSettings, MQTTTopicSUD
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from dataLog.device.device_service import *
from deviceControl.serviceDeviceControl.siteinfor_service import *

async def start_mqtt_service():
    log_device_instance = LogDevice()
    mqtt_handler_instance = MQTTHandler(log_device_instance)
    log_all_device_instance = LogAllDevice(log_device_instance)
    log_mptt_device_instance = LogMPTTDevice(log_device_instance)
    
    project_setup_config = await ProjectSetup.get_project_setup_values()
    time_interval_log_device = await ProjectSetup.get_time_interval_logdevice()
    if project_setup_config is not None and time_interval_log_device is not None:
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
        scheduler.add_job(log_all_device_instance.insert_list_device_data, 'cron', minute=f'*/{time_interval_log_device}')
        scheduler.add_job(log_mptt_device_instance.insert_list_device_mptt_data, 'cron', minute=f'*/{time_interval_log_device}')
        scheduler.start()
        # Sud message
        tasks = []
        tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(mqtt_service,time_interval_log_device))
        await asyncio.gather(*tasks, return_exceptions=False)
    await asyncio.sleep(0.05)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
asyncio.run(start_mqtt_service())
