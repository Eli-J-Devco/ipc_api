# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import os
import sys
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config , DBSessionManager
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)
from dbService.deviceList import deviceListService
from dbService.projectSetup import ProjectSetupService
from dbService.deviceType import deviceTypeService

class ValueEnergySystemClass:
    def __init__(self):
        pass
    @staticmethod
    async def ValueEnergySystemMain(mqtt_service, messageMQTT, topicFeedBack):
        totalProduction, totalConsumption = await ValueEnergySystemClass.calculate_production_and_consumption(messageMQTT)
        try:
            ObjectSendMQTT = ValueEnergySystemClass.create_message_pud_MQTT(messageMQTT, totalProduction, totalConsumption)
            # Push system_info to MQTT
            MQTTService.push_data_zip(mqtt_service, topicFeedBack, ObjectSendMQTT)
            MQTTService.push_data(mqtt_service, topicFeedBack + "Binh", ObjectSendMQTT)
        except Exception as err:
            print(f"Error MQTT subscribe pudValueProductionAndConsumtionInMQTT: '{err}'")
        # Return the relevant global variables
    @staticmethod
    async def calculate_production_and_consumption(messageMQTT):
        totalProductionTemp = 0.0 
        totalConsumptionTemp = 0.0
        
        if messageMQTT:
            for item in messageMQTT:
                if 'id_device' in item:
                    id_device = item['id_device']
                    result_type_meter = await ValueEnergySystemClass.get_device_type(id_device)
                    if result_type_meter:
                        totalProductionTemp = ValueEnergySystemClass.calculate_production(
                            item, result_type_meter, totalProductionTemp)
                        totalConsumptionTemp = ValueEnergySystemClass.calculate_consumption(
                            item, result_type_meter, totalConsumptionTemp)
        
        return totalProductionTemp, totalConsumptionTemp
    
    async def get_device_type(id_device):
        db_new = await DBSessionManager.get_db()
        result = await deviceTypeService.selectTypeDeviceByID(db_new,id_device)
        return result
    def calculate_production(messageMQTT, result_type_meter ,totalProduction):
        if result_type_meter == "PV System Inverter":
            resultFiltermessageMQTT = [
                field["value"] for param in messageMQTT.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            
            # Kiểm tra xem danh sách có rỗng không
            if resultFiltermessageMQTT:
                if resultFiltermessageMQTT[0] is not None:
                    totalProduction += resultFiltermessageMQTT[0]
            
        return totalProduction

    def calculate_consumption(messageMQTT, result_type_meter,totalConsumption):
        if result_type_meter == "Consumption meter":
            resultFiltermessageMQTT = [
                field["value"] for param in messageMQTT.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            
            # Kiểm tra xem danh sách có rỗng không
            if resultFiltermessageMQTT:
                if resultFiltermessageMQTT[0] is not None:
                    totalConsumption += resultFiltermessageMQTT[0]
            
        return totalConsumption

    def create_message_pud_MQTT(messageMQTT, totalProduction, totalConsumption):
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

    