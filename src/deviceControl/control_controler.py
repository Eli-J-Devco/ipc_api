# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)

from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from cpu.cpu_service import *
from deviceControl.deviceControlService.control_service import *
from deviceControl.deviceControlService.enegy_service import *
from deviceControl.deviceControlService.modedetail_service import *
from deviceControl.deviceControlService.modesystem_service import *
from deviceControl.deviceControlService.processdevice_service import *
from deviceControl.deviceControlService.siteinfor_service import *

class MainClass:
    # initialize the necessary parameters
    async def start_mqtt_service(self):
        project_setup_config = await ProjectSetup.get_project_setup_values()
        if project_setup_config["serial_number"] is not None:
            mqtt_settings = MQTTSettings()
            mqtt_topics = MQTTTopicSUD()
            mqtt_service = MQTTService(
                host=mqtt_settings.MQTT_BROKER,
                port=mqtt_settings.MQTT_PORT,
                username=mqtt_settings.MQTT_USERNAME,
                password=mqtt_settings.MQTT_PASSWORD,
                serial_number=project_setup_config["serial_number"]
            )
            mqtt_service.set_topics(
                mqtt_topics.Control_Setup_Mode_Write,
                mqtt_topics.Project_Get,
                mqtt_topics.Control_Setup_Mode_Write_Detail,
                mqtt_topics.Control_Setup_Auto,
                mqtt_topics.Devices_All,
                mqtt_topics.Control_Feedback,
                mqtt_topics.Control_Feedbacksetup,
                mqtt_topics.Project_Set,
                mqtt_topics.Control_Modify
            )
            # function to send and receive messages using mqtt
            tasks = []
            tasks.append(asyncio.create_task(self.subscribe_to_mqtt_topics(mqtt_service, project_setup_config["serial_number"])))
            await asyncio.gather(*tasks, return_exceptions=False)
    
    # mqtt connection and message processing
    async def subscribe_to_mqtt_topics(self, mqtt_service, serial_number):
        try:
            client = mqttools.Client(
                host=mqtt_service.host,
                port=mqtt_service.port,
                username=mqtt_service.username,
                password=bytes(mqtt_service.password, 'utf-8'),
                subscriptions=mqtt_service.topics,
                connect_delays=[1, 2, 4, 8]
            )
            while True:
                await client.start()
                await self.consume_mqtt_messages(mqtt_service, client, serial_number)
                await client.stop()
        except Exception as err:
            print(f"Error subscribe_to_mqtt_topics: '{err}'")
    
    # decode message
    async def consume_mqtt_messages(self, mqtt_service, client, serial_number):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                
                topic = message.topic
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service, serial_number, topic, payload)
        except Exception as err:
            print(f"Error handle_mqtt_messages: '{err}'")
    
    # run services on user-controlled triggers using mqtt 
    async def handle_mqtt_message(self, mqtt_service, serial_number, topic, message):
        topicSudMQTT = MQTTTopicSUD()
        topicPushMQTT = MQTTTopicPUSH()
        try:
            if topic == serial_number + topicSudMQTT.Control_Setup_Mode_Write:
                await ModeSystem.update_mode_system(mqtt_service, message, topicPushMQTT.Control_Setup_Mode_Feedback)
            elif topic in [serial_number + topicSudMQTT.Control_Feedback, serial_number + topicSudMQTT.Control_Feedbacksetup, serial_number + topicSudMQTT.Control_Modify]:
                await ModeSystem.trigger_system_mode_change(mqtt_service, topicPushMQTT.Control_Setup_Mode_Write)
            elif topic == serial_number + topicSudMQTT.Control_Setup_Mode_Write_Detail:
                await ModeControl.update_mode_control(mqtt_service, message, topicPushMQTT.Control_Setup_Mode_Write_Detail_Feedback)
            elif topic == serial_number + topicSudMQTT.Control_Setup_Auto:
                await ModeControl.update_parameter_control(mqtt_service, message, topicPushMQTT.Control_Setup_Auto_Feedback)
            elif topic == serial_number + topicSudMQTT.Project_Get: 
                await ProjectSetup.publish_project_setup(mqtt_service, topicPushMQTT.Project_Information)
            elif topic == serial_number + topicSudMQTT.Project_Set:
                await ProjectSetup.insert_project_setup_info(mqtt_service, message, topicPushMQTT.Project_Set_Feedback)
            elif topic == serial_number + topicSudMQTT.Devices_All:
                messageMQTTAllDevice = message
                resultDB = await ProjectSetup.get_project_setup_values()
                if messageMQTTAllDevice:
                    await ProcessSystem.create_message_for_process_systemp(mqtt_service, messageMQTTAllDevice, topicPushMQTT.Control_Process, resultDB)
                    await EnergySystem.calculate_and_publish_production_and_consumption(mqtt_service, messageMQTTAllDevice, topicPushMQTT.Meter_Monitor)
                    await PowerCalculator.calculate_auto_parameters(mqtt_service, messageMQTTAllDevice, topicPushMQTT.Control_WriteAuto, resultDB)
        except Exception as err:
            print(f"Error MQTT subscribe processMessage: '{err}'") 

if __name__ == '__main__':
    main_instance = MainClass()
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main_instance.start_mqtt_service())