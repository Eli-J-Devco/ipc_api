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
from utils.libTime import *
from dataLog.device.device_service import *
from deviceControl.setupSite.setup_site_service import *
from dbService.projectSetup import ProjectSetupService

class MainClass:
    # initialize the necessary parameters
    async def start_mqtt_service(self):
        setup_site_instance = SetupSite()
        mqtt_handler_instance = MQTTHandlerSetupSite(setup_site_instance)
        project_setup_config = await setup_site_instance.get_project_setup_values()
        
        if project_setup_config is not None :
            mqtt_settings = MQTTSettings()
            mqtt_topics = MQTTTopicSUD()
            mqtt_service = MQTTService(
                host=mqtt_settings.MQTT_BROKER,
                port=mqtt_settings.MQTT_PORT,
                username=mqtt_settings.MQTT_USERNAME,
                password=mqtt_settings.MQTT_PASSWORD,
                serial_number=project_setup_config["serial_number"]
            )
            mqtt_service.set_topics(mqtt_topics.Project_Get,mqtt_topics.Project_Set)
            
            # function to send and receive messages using mqtt
            tasks = []
            tasks.append(mqtt_handler_instance.subscribe_to_mqtt_topics(mqtt_service,project_setup_config["serial_number"]))
            await asyncio.gather(*tasks, return_exceptions=False)
        
        await asyncio.sleep(0.05)

if __name__ == '__main__':
    main_instance = MainClass()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())