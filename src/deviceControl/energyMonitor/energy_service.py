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
from dbService.deviceType import deviceTypeService
from configs.config import MQTTSettings, MQTTTopicSUD, MQTTTopicPUSH
logger = logging.getLogger(__name__)
# ==================================================== Caculator Production And Consumtion  ==================================================================
class EnergySystem:
    def __init__(self):
        self.mqtt_topic_sud = MQTTTopicSUD()
        self.mqtt_topic_push = MQTTTopicPUSH()
        self.devicetypeservice = deviceTypeService()
    # Describe ValueEnergySystemMain 
    # 	 * @description ValueEnergySystemMain
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedBack}
    # 	 * @return 
    # 	 */ 
    async def calculate_and_publish_production_and_consumption(self,mqtt_service, messageMQTT, topicFeedBack):
        totalProduction, totalConsumption = await self.calculate_production_and_consumption(messageMQTT)
        try:
            ObjectSendMQTT = self.create_message_pud_MQTT(messageMQTT, totalProduction, totalConsumption)
            # Push system_info to MQTT
            MQTTService.push_data_zip(mqtt_service, topicFeedBack, ObjectSendMQTT)
            MQTTService.push_data(mqtt_service, topicFeedBack + "Binh", ObjectSendMQTT)
        except Exception as err:
            logger.error(f"Error MQTT subscribe pudValueProductionAndConsumtionInMQTT: '{err}'")
    # Describe calculate_production_and_consumption 
    # 	 * @description calculate_production_and_consumption
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageMQTT}
    # 	 * @return totalProductionTemp, totalConsumptionTemp
    # 	 */ 
    async def calculate_production_and_consumption(self,messageMQTT):
        totalProductionTemp = 0.0 
        totalConsumptionTemp = 0.0
        
        if messageMQTT:
            for item in messageMQTT:
                if 'name_device_type' in item:
                    result_type_meter = item["name_device_type"]
                    if result_type_meter:
                        totalProductionTemp = self.calculate_production(
                            item, result_type_meter, totalProductionTemp)
                        totalConsumptionTemp = self.calculate_consumption(
                            item, result_type_meter, totalConsumptionTemp)
        
        return totalProductionTemp, totalConsumptionTemp
    # Describe calculate_production 
    # 	 * @description calculate_production
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageMQTT, result_type_meter ,totalProduction}
    # 	 * @return totalProduction
    # 	 */ 
    def calculate_production(self,messageMQTT, result_type_meter ,totalProduction):
        if result_type_meter == "PV System Inverter":
            resultFiltermessageMQTT = [
                field["value"] for param in messageMQTT.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            if resultFiltermessageMQTT:
                if resultFiltermessageMQTT[0] is not None:
                    totalProduction += resultFiltermessageMQTT[0]
        return totalProduction
    # Describe calculate_consumption 
    # 	 * @description calculate_consumption
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageMQTT, result_type_meter,totalConsumption}
    # 	 * @return totalConsumption
    # 	 */ 
    def calculate_consumption(self,messageMQTT, result_type_meter,totalConsumption):
        if result_type_meter == "Consumption meter":
            resultFiltermessageMQTT = [
                field["value"] for param in messageMQTT.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            if resultFiltermessageMQTT:
                if resultFiltermessageMQTT[0] is not None:
                    totalConsumption += resultFiltermessageMQTT[0]
        return totalConsumption
    # Describe create_message_pud_MQTT 
    # 	 * @description create_message_pud_MQTT
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {messageMQTT, totalProduction, totalConsumption}
    # 	 * @return result message push mqtt
    # 	 */ 
    def create_message_pud_MQTT(self,messageMQTT, totalProduction, totalConsumption):
        predicted_power = 0
        result = {
            "Timestamp": get_utc(),
            "instant": {},
        }
        if messageMQTT:
            for device in messageMQTT:
                if "mppt" in device:
                    for mppt in device["mppt"]:
                        if "power" in mppt:
                            predicted_power += mppt["power"]
        # instant power
        result["instant"]["production"] = round(totalProduction, 4)
        result["instant"]["consumption"] = round(totalConsumption, 4)
        result["instant"]["grid_feed"] = round((totalProduction - totalConsumption), 4)
        result["instant"]["max_production"] = round(predicted_power, 4)
        return result
class MQTTHandlerEnergySystem(EnergySystem):
    def __init__(self, energy_instance):
        self.energy_instance = energy_instance
        
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
            if message :
                await self.energy_instance.calculate_and_publish_production_and_consumption(mqtt_service, message, self.energy_instance.mqtt_topic_push.Meter_Monitor)
                print("monitor energy")
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")