# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import logging
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import DBSessionManager
from utils.MQTTService import *
from utils.libTime import *
from dbService.projectSetup import ProjectSetupService
from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
logger = logging.getLogger(__name__)
# ============================================================== Parametter Mode Detail Systemp ================================
class ModeControl:
    def __init__(self):
        self.mqtt_topic_sud = MQTTTopicSUD()
        self.mqtt_topic_push = MQTTTopicPUSH()
        self.project_setup_service = ProjectSetupService()
    # Describe handleModeDetailChange 
    # 	 * @description handleModeDetailChange
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedback}
    # 	 * @return ModeDetail
    # 	 */ 
    async def update_mode_control(self,mqtt_service, messageMQTT, topicFeedback):
        intComment = 0
        resultDB = []
        db_new=await DBSessionManager.get_db()
        try:
            if messageMQTT and 'control_mode' in messageMQTT:
                ModeDetail = messageMQTT['control_mode'] 
                token = messageMQTT.get("token", "")
                updateModeDetail = {
                        'control_mode': ModeDetail,
                        }
                resultDB = await self.project_setup_service.updateProjectSetup(db_new,updateModeDetail)
                if resultDB is None:
                    intComment = 400 
                else:
                    intComment = 200 
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment, 
                    "token" : token
                }
                MQTTService.push_data_zip(mqtt_service, topicFeedback, objectSend)
                return ModeDetail
        except Exception as err:
            logger.error(f"Error MQTT subscribe processUpdateModeControlDetail: '{err}'")
            return None  
    # Describe handleParametterDetailChange 
    # 	 * @description handleParametterDetailChange
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedback}
    # 	 * @return return {
    #     "value_offset_zero_export": OffsetZeroExport,
    #     "value_power_limit": ValuePowerLimit,
    #     "value_offset_power_limit": OffsetPowerLimit,
    #     "threshold_zero_export": ThresholdZeroExport,
    #       }
    # 	 */ 
    async def update_parameter_control (self,mqtt_service, messageMQTT, topicFeedBack):
        ModeDetail = ""
        intComment = 0
        resultDBZeroExport = []
        resultDBPowerLimit = []
        db_new = await DBSessionManager.get_db()
        result = await self.project_setup_service.selectAllProjectSetup(db_new)
        try:
            if messageMQTT and 'mode' in messageMQTT and 'offset' in messageMQTT :
                ModeDetail = int(messageMQTT['mode'])
                token = messageMQTT.get("token", "")
                if ModeDetail == 1:
                    OffsetZeroExport, ThresholdZeroExport, resultDBZeroExport = await self.update_zero_export_mode (messageMQTT)
                    OffsetPowerLimit = result[0]["value_offset_power_limit"]
                    ValuePowerLimit = result[0]["value_power_limit"]
                elif ModeDetail == 2:
                    OffsetPowerLimit, ValuePowerLimit, resultDBPowerLimit = await self.update_power_limit_mode(messageMQTT)
                    OffsetZeroExport = result[0]["value_offset_zero_export"]
                    ThresholdZeroExport = result[0]["threshold_zero_export"]
                # Feedback to MQTT
                if ((resultDBZeroExport is None and ModeDetail == 1) or 
                    (resultDBPowerLimit is None and ModeDetail == 2) or 
                    ValuePowerLimit is None ):
                    intComment = 400 
                else:
                    intComment = 200 
                # Object Sent MQTT
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment,
                    "token":token
                }
                # Push MQTT
                MQTTService.push_data_zip(mqtt_service, topicFeedBack, objectSend)
                return {
                    "value_offset_zero_export": OffsetZeroExport,
                    "value_power_limit": ValuePowerLimit,
                    "value_offset_power_limit": OffsetPowerLimit,
                    "threshold_zero_export": ThresholdZeroExport,
                }
        except Exception as err:
            logger.error(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'")
            return None
    # Describe update_zero_export_mode  
    # 	 * @description update_zero_export_mode 
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {message}
    # 	 * @return ValueOffsetTemp, ValueThresholdTemp, ResultQuery
    # 	 */ 
    async def update_zero_export_mode (self,message):
        db_new = await DBSessionManager.get_db()
        ValueOffsetTemp = message.get("offset", 0)
        ValueThresholdTemp = message.get("threshold", 0)
        updateZeroExport = {
                'value_offset_zero_export': ValueOffsetTemp,
                'threshold_zero_export': ValueThresholdTemp,
            }
        ResultQuery = await self.project_setup_service.updateProjectSetup(db_new,updateZeroExport)
        return ValueOffsetTemp, ValueThresholdTemp, ResultQuery
    # Describe update_power_limit_mode 
    # 	 * @description update_power_limit_mode
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {message}
    # 	 * @return ValueOffsetTemp, ValuePowerLimit, ResultQuery
    # 	 */ 
    async def update_power_limit_mode(self, message):
        db_new = await DBSessionManager.get_db()
        ValueOffsetTemp = message.get("offset", 0)
        ValuePowerLimitTemp = message.get("value", 0)
        
        if ValuePowerLimitTemp is not None:
            ValuePowerLimit = ValuePowerLimitTemp - (ValuePowerLimitTemp * ValueOffsetTemp) / 100
            updatePowerLimit = {
                    'value_power_limit': ValuePowerLimitTemp,
                    'value_offset_power_limit': ValueOffsetTemp,
                    # Add other fields if needed
                }
            ResultQuery = await self.project_setup_service.updateProjectSetup(db_new,updatePowerLimit)
            return ValueOffsetTemp, ValuePowerLimit, ResultQuery
        
        return ValueOffsetTemp, None, None
class MQTTHandlerModeControl(ModeControl):
    def __init__(self, mode_control_instance):
        self.mode_control_instance = mode_control_instance
        
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
            if topic == serial + self.mode_control_instance.mqtt_topic_sud.Control_Setup_Mode_Write_Detail:
                await self.mode_control_instance.update_mode_control(mqtt_service, message, self.mode_control_instance.mqtt_topic_push.Control_Setup_Mode_Write_Detail_Feedback)
                print("update mode control suscessfully")
            elif topic == serial + self.mode_control_instance.mqtt_topic_sud.Control_Setup_Auto:
                await self.mode_control_instance.update_parameter_control(mqtt_service, message, self.mode_control_instance.mqtt_topic_push.Control_Setup_Auto_Feedback)
                print("update parameter control suscessfully")
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")