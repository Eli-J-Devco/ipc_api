
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
from deviceControl.control_service import *
# ==================================================== Get List All Device ==================================================================
class GetListAllDeviceClass:
    def __init__(self):
        pass
    async def GetListAllDeviceMain(mqtt_service, messageAllDevice, topicFeedback , ArlamLow , ArlamHigh,TotalPoductionINV , ModeSystem ,SystemPerformance):
        ArrayDeviceList = []
        TotalPowerINV = 0.0
        TotalPowerINVMan = 0.0
        # Get Information about the device
        if messageAllDevice and isinstance(messageAllDevice, list):
            for item in messageAllDevice:
                device_info = GetListAllDeviceClass.extract_device_all_info(item)
                device_auto_info = GetListAutoDeviceClass.getListDeviceAutoModeInALLInv(item)
                TotalPowerINVAuto = GetListAutoDeviceClass.calculate_total_power_inv_auto(device_auto_info)
                if device_info:
                    ArrayDeviceList.append(device_info)
        # Calculate the sum of wmax values of all inv in the system
        TotalPowerINV, TotalPowerINVMan = GetListAllDeviceClass.calculate_total_wmax(ArrayDeviceList, TotalPowerINVAuto)
        # Call the update_system_performance function and get the return value
        SystemPerformance, statusString, statusInt = GetListAllDeviceClass.update_system_performance(
            ModeSystem,
            SystemPerformance,
            TotalPowerINV,
            TotalPoductionINV,
            ArlamLow,
            ArlamHigh
        )
        # Message Public MQTT
        result = {
            "ModeSystempCurrent": ModeSystem,
            "devices": ArrayDeviceList,
            "total_max_power": TotalPowerINV,
            "total_max_power_man": TotalPowerINVMan,
            "total_max_power_auto": TotalPowerINVAuto,
            "system_performance": {
                "performance": SystemPerformance,
                "message": statusString,
                "status": statusInt
            }
        }
        # Public MQTT
        MQTTService.push_data_zip(mqtt_service, topicFeedback, result)
        MQTTService.push_data(mqtt_service, topicFeedback + "Binh", result)
        return TotalPowerINV,TotalPowerINVMan,SystemPerformance
    
    def extract_device_all_info(item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom_temp = item['rated_power_custom']
            if p_max_custom_temp != None :
                p_max_custom = p_max_custom_temp
            else:
                p_max_custom = p_max
            p_min_percent = item['min_watt_in_percent']
            device_name = item['device_name']
            results_device_type = item['name_device_type']
            
            if results_device_type == "PV System Inverter":
                operator, wmax, capacity_power, real_power = GetListAllDeviceClass.get_device_parameters(item)
                
                if status_device == 'offline':
                    real_power = 0.0
                    operator = "off"
                    
                p_min = GetListAllDeviceClass.calculate_p_min(p_max_custom, p_min_percent)
                
                return {
                    'id_device': id_device,
                    'device_name': device_name,
                    'mode': mode,
                    'status_device': status_device,
                    'operator': operator,
                    'capacitypower': capacity_power,
                    'p_max': p_max_custom,
                    'p_min': p_min,
                    'wmax': wmax,
                    'realpower': real_power,
                    'timestamp': get_utc(),
                }
        return None
    @staticmethod
    def get_device_parameters(item):
        stringOperatorText = {
            0: "shutting down",
            1: "shutting down",
            4: "running",
            5: "running",
            6: "shutting down",
            7: "fault",
        }
        
        ArrayOperator = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                        for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
        intOperator = ArrayOperator[0] if ArrayOperator else 0
        operator = stringOperatorText.get(intOperator, "off")
        
        wmax = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                        for field in param.get("fields", []) if field["point_key"] == "WMax"), 0)
        capacity_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                                for field in param.get("fields", []) if field["point_key"] == "PowerOutputCapability"), 0)
        real_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" 
                            for field in param.get("fields", []) if field["point_key"] == "ACActivePower"), 0)

        return operator, wmax, capacity_power, real_power
    @staticmethod
    def calculate_total_wmax(device_list, power_auto):
        total_power_write_inv = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None), 2)
        total_power_manual = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None and device['mode'] == 0), 2)
        total_power = round((total_power_manual + power_auto), 2)
        return total_power, total_power_manual
    @staticmethod
    def calculate_p_min(p_max_custom, p_min_percent):
        return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0
    @staticmethod
    def update_system_performance(current_mode, systemPerformance, total_power_in_all_inv, production_system, low_performance_threshold, high_performance_threshold):
        if current_mode == 0:
            systemPerformance = (production_system / total_power_in_all_inv) * 100 if total_power_in_all_inv else 0
        
        systemPerformance = round(systemPerformance, 1)
        
        if systemPerformance < low_performance_threshold:
            statusString = "System performance is below expectations."
            statusInt = 0
        elif low_performance_threshold <= systemPerformance < high_performance_threshold:
            statusString = "System performance is meeting"
            statusInt = 1
        else:
            statusString = "System performance is exceeding established thresholds."
            statusInt = 2

        return systemPerformance, statusString, statusInt