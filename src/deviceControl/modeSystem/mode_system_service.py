# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import os
import sys
import logging
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import  DBSessionManager
from utils.MQTTService import *
from utils.libTime import *
from dbService.deviceList import deviceListService
from dbService.projectSetup import ProjectSetupService
from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
logger = logging.getLogger(__name__)
class ModeSystem:
    def __init__(self):
        self.mqtt_topic_sud = MQTTTopicSUD()
        self.mqtt_topic_push = MQTTTopicPUSH()
        self.device_list_service = deviceListService()
        self.project_setup_service = ProjectSetupService()
    # Describe triggerDeviceModeChange 
    # 	 * @description triggerDeviceModeChange
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service,topicFeedback}
    # 	 * @return 
    # 	 */ 
    async def trigger_system_mode_change(self,mqtt_service,topicFeedback):
        try:
            db_new=await DBSessionManager.get_db()
            modes = await self.device_list_service.selectUniqueModesByDeviceType(db_new)
            if len(modes) == 1:
                if 0 in modes:
                    data_send = {"id_device": "Systemp", "mode": 0}
                elif 1 in modes:
                    data_send = {"id_device": "Systemp", "mode": 1}
            else:
                data_send = {"id_device": "Systemp", "mode": 2}
            MQTTService.push_data_zip(mqtt_service,topicFeedback, data_send)
        except asyncio.TimeoutError:
            logger.error("Timeout waiting for data from MySQL")
    # Describe handleModeSystemChange 
    # 	 * @description handleModeSystemChange
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedback}
    # 	 * @return modeSysTemp
    # 	 */ 
    async def update_mode_system(self,mqtt_service, messageMQTT, topicFeedback):
        db_new=await DBSessionManager.get_db()
        if messageMQTT.get('id_device') == 'Systemp':
            modeSysTemp = messageMQTT.get('mode')
            token = messageMQTT.get('token')
            if modeSysTemp in [0, 1, 2]:
                updates = {
                        'mode': modeSysTemp,
                    }
                await self.project_setup_service.updateProjectSetup(db_new,updates)
            else:
                print("Failed to insert data")
            if modeSysTemp in [0, 1]:
                await self.device_list_service.updateDeviceModeByType(db_new, modeSysTemp)
            current_time = get_utc()
            objectSend = {
                "status": 200,
                "confirm_mode": modeSysTemp,
                "time_stamp": current_time,
                "token":token
            } if modeSysTemp in [0, 1, 2] else {
                "status": 400,
                "time_stamp": current_time,
                "token":token
            }
            MQTTService.push_data_zip(mqtt_service, topicFeedback, objectSend)
            return modeSysTemp
        
class MQTTHandlerModeSystem(ModeSystem):
    def __init__(self, mode_system_instance):
        self.mode_system_instance = mode_system_instance
        
    async def subscribe_to_mqtt_topics(self,mqtt_service,serial):
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
                await self.consume_mqtt_messages(mqtt_service, client,serial)
                await client.stop()
        except Exception as err:
            logger.error(f"Error subscribing to MQTT topics: '{err}'")
    
    async def consume_mqtt_messages(self,mqtt_service, client,serial):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    logger.info('Broker connection lost!')
                    break
                topic = message.topic
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service,payload,topic,serial)
        except Exception as err:
            logger.error(f"Error consuming MQTT messages: '{err}'")
    
    async def handle_mqtt_message(self, mqtt_service, message,topic, serial):
        try:
            if topic == serial + self.mode_system_instance.mqtt_topic_sud.Control_Setup_Mode_Write:
                await self.mode_system_instance.update_mode_system(mqtt_service, message, self.mode_system_instance.mqtt_topic_push.Control_Setup_Mode_Feedback)
                print("update mode suscessfully")
            elif topic in [serial + self.mode_system_instance.mqtt_topic_sud.Control_Feedback, serial + self.mode_system_instance.mqtt_topic_sud.Control_Feedbacksetup, serial + self.mode_system_instance.mqtt_topic_sud.Control_Modify]:
                await self.mode_system_instance.trigger_system_mode_change(mqtt_service, self.mode_system_instance.mqtt_topic_push.Control_Setup_Mode_Write)
                print("triger mode suscessfully")
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")