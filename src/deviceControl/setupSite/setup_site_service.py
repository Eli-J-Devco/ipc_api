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
from utils.MQTTService import *
from deviceControl.setupSite.db_sql import *
from utils.libTime import *
from dbService.projectSetup import ProjectSetupService
from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
from configs.config import orm_provider as config
logger = logging.getLogger(__name__)
class SetupSite:
    def __init__(self):
        self.mqtt_topic_sud = MQTTTopicSUD()
        self.mqtt_topic_push = MQTTTopicPUSH()
        self.project_setup_service = ProjectSetupService()
    # Describe initializeValueControlAuto 
    # 	 * @description initializeValueControlAuto
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {}
    # 	 * @return return {
                #     "serial_number": serialNumber,
                #     "mode": ModeSystemp,
                #     "control_mode": gIntControlModeDetail,
                #     "value_offset_zero_export": OffsetZeroExport,
                #     "value_power_limit": PowerLimit,
                #     "value_offset_power_limit": OffsetPowerLimit,
                #     "threshold_zero_export": ThresholdZeroExport,
                #     "low_performance": LowPerformance,
                #     "high_performance": ArlamHighPerformance,
                # }
    # 	 */ 
    async def get_project_setup_values(self):
        try:
            db_new = await config.get_db()
            resultDB = await self.project_setup_service.selectAllProjectSetup(db_new)
            if resultDB and len(resultDB) > 0:
                project_setup = resultDB[0]
                return {
                    "serial_number": project_setup.serial_number,
                    "mode": project_setup.mode,
                    "control_mode": project_setup.control_mode,
                    "value_offset_zero_export": project_setup.value_offset_zero_export,
                    "value_power_limit": project_setup.value_power_limit,
                    "value_offset_power_limit": project_setup.value_offset_power_limit,
                    "threshold_zero_export": project_setup.threshold_zero_export,
                    "low_performance": project_setup.low_performance,
                    "high_performance": project_setup.high_performance,
                }
            else:
                logger.info("No data found in resultDB.")
                return None
        except Exception as err:
            logger.error(f"Error MQTT subscribe initializeValueControlAuto: '{err}'")
            return None 
    # Describe pudFeedBackProjectSetup 
    # 	 * @description pudFeedBackProjectSetup
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service,topicFeedBack}
    # 	 * @return 
    # 	 */ 
    async def publish_project_setup(self,mqtt_service,topicFeedBack):
        try :
            db_new = await config.get_db()
            resultDB = await self.project_setup_service.selectAllProjectSetup(db_new)
            if resultDB:
                try:
                    OjectSentMQTT = resultDB[0]
                    
                    data_to_send = {
                    "mqtt": [
                        {"time_stamp": get_utc()},
                        {"status": 200}
                    ],
                    **OjectSentMQTT.dict()
                    }
                    MQTTService.push_data_zip(mqtt_service,topicFeedBack, data_to_send)
                except Exception as err:
                    print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
        except Exception as err:
            data_send = {
                "mqtt": [
                        {"time_stamp" : get_utc()},
                        {"status":400}]
                        }
            MQTTService.push_data_zip(mqtt_service,topicFeedBack,data_send)
    # Describe insertInformationProjectSetup 
    # 	 * @description insertInformationProjectSetup
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedBack}
    # 	 * @return 
    # 	 */ 
    @staticmethod
    async def insert_project_setup_info(mqtt_service, messageMQTT, topicFeedBack):
        try:
            resultSet = messageMQTT.get('parameter', {})
            resultSet.pop('mqtt', None)
            token = messageMQTT.get('token', "")
            if resultSet:
                update_fields = ", ".join([f"{field} = %s" for field, value in resultSet.items()])
                update_values = [value for field, value in resultSet.items()]
                values = [tuple(update_values)]
                query = f"UPDATE project_setup SET {update_fields}"
                if query and update_values:
                    result = update_project_setup(query, values)
                if result is not None:
                    status = 200
                else:
                    status = 400
                current_time = get_utc()
                data_send = {
                    "status": status,
                    "time_stamp": current_time,
                    "token": token,
                }
                MQTTService.push_data_zip(mqtt_service, topicFeedBack, data_send)
        except Exception as err:
            logger.error(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")
    async def get_time_interval_logdevice(self):
        try :
            db_new = await config.get_db()
            resultDB = await self.project_setup_service.selectTimeLogInterval(db_new)
            if resultDB:
                try:
                    time = resultDB[0]
                    return time
                except Exception as err:
                    logger.error(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
        except Exception as err:
            logger.error(f"Error MQTT subscribe get_time_interval_logdevice: '{err}'")
            return None 
class MQTTHandlerSetupSite(SetupSite):
    def __init__(self, setup_site_instance):
        self.setup_site_instance = setup_site_instance
        
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
            if topic == serial + self.setup_site_instance.mqtt_topic_sud.Project_Get: 
                await self.setup_site_instance.publish_project_setup(mqtt_service, self.setup_site_instance.mqtt_topic_push.Project_Information)
                print("get information site successfully")
            elif topic == serial + self.setup_site_instance.mqtt_topic_sud.Project_Set:
                await self.setup_site_instance.insert_project_setup_info(mqtt_service, message, self.setup_site_instance.mqtt_topic_push.Project_Set_Feedback)
                print("set information site successfully")
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")
    
    