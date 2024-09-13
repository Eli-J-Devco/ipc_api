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

arr = sys.argv  # Id Channel
IdChannel = arr[1]
from configs.config import MQTTSettings, MQTTTopicSUD, FolderSetting
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from dataLog.file.file_service import *
from deviceControl.deviceControlService.siteinfor_service import *

class MainClass:
    def __init__(self, id_channel):
        self.id_channel = id_channel
    
    # initialize the necessary parameters
    async def start_mqtt_service(self):
        log_file_instance = LogFile()
        mqtt_handler_instance = MQTTHandler(log_file_instance)
        process_logfile_instance = ProcessLogFile(log_file_instance)
        
        project_setup_config = await ProjectSetup.get_project_setup_values()
        time_interval_log_device = await ProjectSetup.get_time_interval_logdevice()
        type_of_file = await log_file_instance.get_type_of_file(self.id_channel)
        
        if project_setup_config is not None and time_interval_log_device is not None:
            folder_parameter = FolderSetting()
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
            
            # run services on cycle time
            scheduler = AsyncIOScheduler()
            scheduler.add_job(process_logfile_instance.create_file_log,'cron',minute=f'*/{time_interval_log_device}',
                args=[folder_parameter.Path_File_Log, folder_parameter.Head_File_Log, self.id_channel, type_of_file])
            scheduler.start()
            
            # function to send and receive messages using mqtt
            tasks = []
            tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(
                mqtt_service,
                time_interval_log_device,
                log_file_instance,
                self.id_channel,
                folder_parameter.Head_File_Log,
                type_of_file
            ))
            await asyncio.gather(*tasks, return_exceptions=False)
        
        await asyncio.sleep(0.05)

if __name__ == '__main__':
    id_channel = sys.argv[1]
    main_instance = MainClass(id_channel)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())