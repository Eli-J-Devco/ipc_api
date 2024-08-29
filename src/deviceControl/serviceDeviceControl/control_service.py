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

# ==================================================== Get List Auto Device  ==================================================================
class GetListAutoDeviceClass:
    def __init__(self):
        pass
    @staticmethod
    async def getListDeviceAutoModeInALLInv(messageAllDevice):
        ArayyDeviceList = []
        if messageAllDevice and isinstance(messageAllDevice, list):
            for item in messageAllDevice:
                device_info = GetListAutoDeviceClass.extract_device_auto_info(item)
                if not device_info:
                    continue
                # Get Information Each Device 
                id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type = device_info
                # Check Device Auto 
                if GetListAutoDeviceClass.is_device_controlable(results_device_type, status_device, mode, operator):
                    ArayyDeviceList.append({
                        'id_device': id_device,
                        'mode': mode,
                        'status_device': status_device,
                        'p_max': p_max_custom,
                        'p_min': p_min,
                        'controlinv': value,
                        'operator': operator,
                        'slope': slope,
                    })
        return ArayyDeviceList
    def extract_device_auto_info(messageMQTT):
        if 'id_device' in messageMQTT and 'mode' in messageMQTT and 'status_device' in messageMQTT:
            id_device = messageMQTT['id_device']
            mode = messageMQTT['mode']
            status_device = messageMQTT['status_device']
            p_max = messageMQTT['rated_power']
            p_max_custom_temp = messageMQTT['rated_power_custom']
            if p_max_custom_temp != None :
                p_max_custom = p_max_custom_temp
            else:
                p_max_custom = p_max
            p_min_percent = messageMQTT['min_watt_in_percent']
            p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
            value = GetListAutoDeviceClass.get_device_value(messageMQTT, "ControlINV")
            if value is None:
                return None
            operator = GetListAutoDeviceClass.get_device_value(messageMQTT, "OperatingState")
            if operator is None:
                return None
            slope = GetListAutoDeviceClass.get_device_value(messageMQTT, "WMax", field_key='slope')
            if slope is None:
                return None
            results_device_type = messageMQTT.get('name_device_type')
            if results_device_type is None:
                return None
            return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
        return None
    def get_device_value(item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None

    def is_device_controlable(results_device_type, status_device, mode, operator):
        return (results_device_type == "PV System Inverter" and 
                status_device == 'online' and 
                mode == 1 and 
                operator not in [7, 8])
    @staticmethod
    def calculate_total_power_inv_auto(ArayyDeviceList):
        if ArayyDeviceList:
            total_power = round(sum(device['p_max'] for device in ArayyDeviceList if device['p_max'] is not None), 2)
            return total_power
        return 0
    
# ==================================================== Caculator PowerLit And ZeroExport  ==================================================================
class caculatorPowerClass:
    def __init__(self):
        pass
    @staticmethod
    def process_device_powerlimit_info(device):
        id_device = device["id_device"]
        mode = device["mode"]
        intPowerMaxOfInv = float(device["p_max"])
        return id_device, mode, intPowerMaxOfInv
    @staticmethod
    def calculate_power_value(intPowerMaxOfInv, modeSystem, TotalPowerInInvInManMode, TotalPowerInInvInAutoMode, Setpoint):
        # Tính toán hiệu suất cho thiết bị
        if modeSystem == 1:
            Efficiency = (Setpoint / TotalPowerInInvInAutoMode)
        else:
            Efficiency = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
        # Công suất của thiết bị bằng hiệu suất nhân với công suất tối đa.
        if 0 <= Efficiency <= 1:
            return Efficiency * intPowerMaxOfInv
        elif Efficiency < 0:
            return 0
        else:
            return intPowerMaxOfInv
    @staticmethod
    def create_control_item(ModeSystemDetail ,device, PowerForEachInv, Setpoint, TotalPowerInInvInManMode, ValueProduction):
        if ModeSystemDetail == 1 :
            status = "Zero Export"
        else:
            status = " Power Limit "
        id_device = device["id_device"]
        mode = device["mode"]
        ItemlistInvControlPowerLimitMode = {
            "id_device": id_device,
            "mode": mode,
            "time": get_utc(),
            "status": status,
            "setpoint": Setpoint - TotalPowerInInvInManMode,
            "feedback": ValueProduction,
            "parameter": []
        }
        # Tạo mục cho thiết bị
        if device['controlinv'] == 1:
            ItemlistInvControlPowerLimitMode["parameter"].append({"id_pointkey": "WMax", "value": PowerForEachInv})
        elif device['controlinv'] == 0:
            ItemlistInvControlPowerLimitMode["parameter"].extend([
                {"id_pointkey": "ControlINV", "value": 1},
                {"id_pointkey": "WMax", "value": PowerForEachInv}
            ])
        return ItemlistInvControlPowerLimitMode
    async def calculate_setpoint( modeSystem, ValueConsump, ValueTotalPowerInInvInManMode,
                                    gListMovingAverageConsumption, gMaxValueChangeSetpoint, ValueOffetConsump):
        ConsumptionAfterSudOfset = 0.0
        if modeSystem == 1:
            gListMovingAverageConsumption.append(ValueConsump)
        else:
            gListMovingAverageConsumption.append(ValueConsump - ValueTotalPowerInInvInManMode)

        if ValueConsump > ValueTotalPowerInInvInManMode:
            intAvgValueComsumtion = sum(gListMovingAverageConsumption) / len(gListMovingAverageConsumption)
        else:
            intAvgValueComsumtion = 0

        if not hasattr(caculatorPowerClass.calculate_setpoint, 'last_setpoint'):
            caculatorPowerClass.calculate_setpoint.last_setpoint = intAvgValueComsumtion
        
        new_setpoint = intAvgValueComsumtion
        Setpoint = max(
            caculatorPowerClass.calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
            min(caculatorPowerClass.calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        caculatorPowerClass.calculate_setpoint.last_setpoint = Setpoint
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump) / 100)
        if Setpoint:
            Setpoint -= Setpoint * ValueOffetConsump / 100
        return Setpoint, ConsumptionAfterSudOfset

    
