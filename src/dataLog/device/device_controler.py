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

from configs.config import MQTTSettings, MQTTTopicSUD
from utils.MQTTService import *
from utils.libTime import *
from dataLog.device.device_service import *
from deviceControl.setupSite.setup_site_service import *
from logger.logger import setup_logging

class MainClass:
    def __init__(self):
        self.current_time_interval = None
        
    # initialize the necessary parameters
    async def start_mqtt_service(self):
        log_device_instance = LogDevice()
        mqtt_handler_instance = MQTTHandler(log_device_instance)
        log_all_device_instance = LogAllDevice(log_device_instance)
        log_mptt_device_instance = LogMPTTDevice(log_device_instance)
        setup_site_instance = SetupSite()
        project_setup_config = await setup_site_instance.get_project_setup_values()
        time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
        setup_logging(file_name="logdevice", log_path=os.path.join(pathlib.Path(__file__).parent.absolute(), "logs"))
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
            
            # run services on cycle time
            self.scheduler = AsyncIOScheduler()
            self.scheduler.add_job(log_all_device_instance.insert_list_device_data, 'cron', minute=f'*/{time_interval_log_device}',id='log_device')
            self.scheduler.add_job(log_mptt_device_instance.insert_list_device_mptt_data, 'cron', minute=f'*/{time_interval_log_device}',id='log_device_mptt')
            self.scheduler.start()
            # update parameters db init 
            asyncio.create_task(self.update_parameter(setup_site_instance, log_all_device_instance,log_mptt_device_instance))
            # function to send and receive messages using mqtt
            tasks = []
            tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(mqtt_service, time_interval_log_device))
            await asyncio.gather(*tasks, return_exceptions=False)
        await asyncio.sleep(0.05)
        
    async def update_parameter(self, setup_site_instance, log_all_device_instance,log_mptt_device_instance):
        while True:
            try:
                time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
                if time_interval_log_device != self.current_time_interval and time_interval_log_device is not None:
                    self.current_time_interval = time_interval_log_device 
                    # stop jod current 
                    self.scheduler.remove_job('log_device')
                    self.scheduler.remove_job('log_device_mptt')
                    # run new job 
                    self.scheduler.add_job(log_all_device_instance.insert_list_device_data,'cron',minute=f'*/{time_interval_log_device}',id='log_device')
                    self.scheduler.add_job(log_mptt_device_instance.insert_list_device_mptt_data,'cron',minute=f'*/{time_interval_log_device}',id='log_device_mptt')
                await asyncio.sleep(50) # check 50s 
            except Exception as e:
                print("Error in update_parameter:", e)
                
if __name__ == '__main__':
    main_instance = MainClass()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())
