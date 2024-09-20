# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# ********************************************************

import asyncio
import os
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pathlib
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)

arr = sys.argv  # Id Channel
IdChannel = arr[1]
from configs.config import MQTTSettings, MQTTTopicSUD, FolderSetting
from utils.MQTTService import *
from utils.libTime import *
from dataLog.file.file_service import *
from deviceControl.setupSite.setup_site_service import *
from utils.logger_manager import setup_logger

LOGGER = setup_logger(module_name='file')
LOGGER.warn(f'--- init ---')
class MainClass:
    def __init__(self, id_channel):
        self.id_channel = id_channel
        self.current_time_interval = None

    async def start_mqtt_service(self):
        log_file_instance = LogFile()
        mqtt_handler_instance = MQTTHandler(log_file_instance)
        process_logfile_instance = ProcessLogFile(log_file_instance)
        setup_site_instance = SetupSite()
        project_setup_config = await setup_site_instance.get_project_setup_values()
        time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
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
            mqtt_service.set_topics(mqtt_topics.Devices_All)

            self.scheduler = AsyncIOScheduler()
            self.scheduler.add_job(process_logfile_instance.create_file_log,'cron',minute=f'*/{time_interval_log_device}',
                args=[folder_parameter.Path_File_Log, folder_parameter.Head_File_Log, self.id_channel, type_of_file] ,id='log_job')
            self.scheduler.start()

            # update parameters db init 
            asyncio.create_task(self.update_parameter(setup_site_instance, process_logfile_instance, folder_parameter.Path_File_Log, folder_parameter.Head_File_Log, type_of_file))
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

    async def update_parameter(self, setup_site_instance, process_logfile_instance, Path_File_Log, Head_File_Log, type_of_file):
        while True:
            try:
                time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
                if time_interval_log_device != self.current_time_interval and time_interval_log_device is not None:
                    self.current_time_interval = time_interval_log_device 

                    self.scheduler.remove_job('log_job') # stop jod current 
                    self.scheduler.add_job(process_logfile_instance.create_file_log,'cron',minute=f'*/{time_interval_log_device}',
                    args=[Path_File_Log,Head_File_Log, self.id_channel, type_of_file] ,id='log_job') # run new job 
                await asyncio.sleep(50) # check 50s 
            except Exception as e:
                print("Error in update_parameter:", e)

if __name__ == '__main__':
    id_channel = sys.argv[1]
    main_instance = MainClass(id_channel)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())
