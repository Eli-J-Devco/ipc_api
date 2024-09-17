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
from configs.config import orm_provider as config
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from dataSync.sync_service import *
from dataLog.file.file_service import *
from deviceControl.setupSite.setup_site_service import *

class MainClass:
    def __init__(self, id_channel):
        self.id_channel = id_channel
        self.current_time_interval = None
        self.time_sync = None
        self.time_interval = None
    # initialize the necessary parameters
    async def start_mqtt_service(self):
        sync_data_instance = SyncData()
        log_file_instance = LogFile()
        mqtt_handler_instance = MQTTHandler1(sync_data_instance)
        setup_site_instance = SetupSite()
        db_new = await config.get_db()
        project_setup_config = await setup_site_instance.get_project_setup_values()
        time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
        time_sync = await ProjectSetupService.select_time_sync_cloud(db_new)
        time_interval = sync_data_instance.get_cycle_sync(time_sync, time_interval_log_device)
        type_of_file = await log_file_instance.get_type_of_file(self.id_channel)

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
            
            # run services on cycle time
            scheduler = AsyncIOScheduler()
            if time_sync in [0, 23]:
                scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'cron', hour=time_sync, args=[self.id_channel, type_of_file],id='sync1_log')
            elif time_sync in [95, 96, 99]:
                scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', hours=time_interval, args=[self.id_channel, type_of_file],id='sync2_log')
            elif time_sync in [97, 98]:
                scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', minutes=time_interval, args=[self.id_channel, type_of_file],id='sync3_log')
            scheduler.start()
            
            # update parameters db init 
            asyncio.create_task(self.update_parameter(setup_site_instance, sync_data_instance, type_of_file))
            
            # function to send and receive messages using mqtt
            tasks = []
            type_of_file = 1
            tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(mqtt_service, time_sync, self.id_channel, type_of_file, project_setup_config["serial_number"]))
            await asyncio.gather(*tasks, return_exceptions=False)
        await asyncio.sleep(0.05)
        
    async def update_parameter(self, setup_site_instance, sync_data_instance, type_of_file):
        while True:
            try:
                db_new = await config.get_db()
                time_interval_log_device = await setup_site_instance.get_time_interval_logdevice()
                time_sync = await ProjectSetupService.select_time_sync_cloud(db_new)
                time_interval = sync_data_instance.get_cycle_sync(time_sync, time_interval_log_device)
                
                if time_interval_log_device != self.current_time_interval or time_sync != self.time_sync:
                    self.current_time_interval = time_interval_log_device 
                    self.time_sync = time_sync
                    self.time_interval = time_interval
                    # stop jod current 
                    self.scheduler.remove_job('sync1_log')
                    self.scheduler.remove_job('sync2_log')
                    self.scheduler.remove_job('sync3_log')
                    # run new job 
                    self.scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging,'cron',hour=f'*/{time_interval_log_device}', args=[self.id_channel, type_of_file],id='sync1_log')
                    self.scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', hours=time_interval, args=[self.id_channel, type_of_file],id='sync2_log')
                    self.scheduler.add_job(sync_data_instance.process_sync_file_log_to_stagging, 'interval', minutes=time_interval, args=[self.id_channel, type_of_file],id='sync3_log')
                await asyncio.sleep(50) # check 50s 
            except Exception as e:
                print("Error in update_parameter:", e)
                
if __name__ == '__main__':
    id_channel = sys.argv[1]
    main_instance = MainClass(id_channel)
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())