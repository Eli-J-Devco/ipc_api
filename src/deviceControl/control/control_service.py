# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import base64
import collections
import datetime
import gzip
import json
import logging
import os
import platform
import sys
from datetime import datetime

import mqttools
import psutil
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)


# ============================================================== Mode Systemp ================================
class ModeSystem:
    def __init__(self):
        pass

    async def processModeChange(self,mqtt_service, gArrayMessageChangeModeSystemp, topicFeedbackModeSystemp):
        if gArrayMessageChangeModeSystemp.get('id_device') == 'Systemp':
            gStringModeSysTemp = gArrayMessageChangeModeSystemp.get('mode')
            if gStringModeSysTemp in [0, 1, 2]:
                await self.update_system_mode(gStringModeSysTemp)
            else:
                print("Failed to insert data")
            if gStringModeSysTemp in [0, 1]:
                await self.update_device_mode(gStringModeSysTemp)
            current_time = get_utc()
            objectSend = {
                "status": 200,
                "confirm_mode": gStringModeSysTemp,
                "time_stamp": current_time,
            } if gStringModeSysTemp in [0, 1, 2] else {
                "status": 400,
                "time_stamp": current_time,
            }
            MQTTService.push_data_zip(mqtt_service, topicFeedbackModeSystemp, objectSend)
            return gStringModeSysTemp

    async def update_system_mode(self, mode):
        querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
        return MySQL_Insert_v5(querysystemp, (mode,))

    async def update_device_mode(self, mode):
        querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';"
        return MySQL_Insert_v5(querydevice, (mode,))
# ============================================================== Parametter Mode Detail Systemp ================================
class ModeDetailHandler:
    def __init__(self):
        pass
    
    async def handle_zero_export_mode( message):
        ValueOffsetTemp = message.get("offset", 0)
        ValueThresholdTemp = message.get("threshold", 0)
        
        # Result Query 
        ResultQuery = await MySQL_Update_V1(
            "UPDATE project_setup SET value_offset_zero_export = %s, threshold_zero_export = %s",
            (ValueOffsetTemp, ValueThresholdTemp)
        )
        return ValueOffsetTemp, ValueThresholdTemp, ResultQuery

    async def handle_power_limit_mode( message, TotalPower):
        ValueOffsetTemp = message.get("offset", 0)
        ValuePowerLimitTemp = message.get("value", 0)
        
        if ValuePowerLimitTemp is not None and ValuePowerLimitTemp <= TotalPower:
            ValuePowerLimit = ValuePowerLimitTemp - (ValuePowerLimitTemp * ValueOffsetTemp) / 100
            # Result Query 
            ResultQuery = await MySQL_Update_V1(
                "UPDATE project_setup SET value_power_limit = %s, value_offset_power_limit = %s",
                (ValuePowerLimitTemp, ValueOffsetTemp)
            )
            return ValueOffsetTemp, ValuePowerLimit, ResultQuery
        
        return ValueOffsetTemp, None, None

# ==================================================== Get List Auto Device  ==================================================================
class GetListAutoDevice:
    def __init__(self):
        pass
    def extract_device_auto_info(self, item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom = item.get('rated_power_custom', p_max)
            p_min_percent = item['min_watt_in_percent']
            p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
            value = self.get_device_value(item, "ControlINV")
            if value is None:
                return None
            operator = self.get_device_value(item, "OperatingState")
            if operator is None:
                return None
            slope = self.get_device_value(item, "WMax", field_key='slope')
            if slope is None:
                return None
            results_device_type = item.get('name_device_type')
            if results_device_type is None:
                return None
            return id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type
        return None
    def get_device_value(self, item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None

    def is_device_controlable(self, results_device_type, status_device, mode, operator):
        return (results_device_type == "PV System Inverter" and 
                status_device == 'online' and 
                mode == 1 and 
                operator not in [7, 8])
    def get_device_value(self, item, point_key, field_key='value'):
        array = [field[field_key] for param in item.get("parameters", []) if param["name"] == "Basic" 
                    for field in param.get("fields", []) if field["point_key"] == point_key]
        return array[0] if array else None
    
# ==================================================== Get List All Device ==================================================================
class GetListAllDevice:
    def __init__(self):
        pass

    def extract_device_all_info(self, item):
        if 'id_device' in item and 'mode' in item and 'status_device' in item:
            id_device = item['id_device']
            mode = item['mode']
            status_device = item['status_device']
            p_max = item['rated_power']
            p_max_custom = item.get('rated_power_custom', p_max)
            p_min_percent = item['min_watt_in_percent']
            device_name = item['device_name']
            results_device_type = item['name_device_type']
            
            if results_device_type == "PV System Inverter":
                operator, wmax, capacity_power, real_power = self.get_device_parameters(item)
                
                if status_device == 'offline':
                    real_power = 0.0
                    operator = "off"
                    
                p_min = self.calculate_p_min(p_max_custom, p_min_percent)
                
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
                    'timestamp': self.get_utc(),
                }
        return None

    def get_device_parameters(self, item):
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

    def calculate_total_wmax(self, device_list, power_auto):
        total_power_write_inv = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None), 2)
        total_power_manual = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None and device['mode'] == 0), 2)
        total_power = round((total_power_manual + power_auto), 2)
        return total_power, total_power_manual

    def calculate_p_min(self, p_max_custom, p_min_percent):
        return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0

    def update_system_performance(self, current_mode, systemPerformance, total_power_in_all_inv, production_system, low_performance_threshold, high_performance_threshold):
        if current_mode == 0:
            systemPerformance = (production_system / total_power_in_all_inv) * 100 if total_power_in_all_inv else 0
        
        systemPerformance = round(systemPerformance, 1)
        
        if systemPerformance < low_performance_threshold:
            StringMessageStatusSystemPerformance = "System performance is below expectations."
            intStatusSystemPerformance = 0
        elif low_performance_threshold <= systemPerformance < high_performance_threshold:
            StringMessageStatusSystemPerformance = "System performance is meeting"
            intStatusSystemPerformance = 1
        else:
            StringMessageStatusSystemPerformance = "System performance is exceeding established thresholds."
            intStatusSystemPerformance = 2

        return systemPerformance, StringMessageStatusSystemPerformance, intStatusSystemPerformance
    
# ==================================================== Get Value Metter  ==================================================================
class ValueEnergySystem:
    def __init__(self):
        pass

    def get_device_type(id_device):
        return MySQL_Select(
            "SELECT `device_type`.`name` FROM `device_type` "
            "INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id "
            "WHERE `device_list`.id = %s",
            (id_device,)
        )

    def calculate_production( item, result_type_meter, IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production, current_time):
        if result_type_meter[0]["name"] == "PV System Inverter":
            ArrayValueProduction = [
                field["value"] for param in item.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            if ArrayValueProduction and ArrayValueProduction[0] is not None:
                IntTotalValueProduction += ArrayValueProduction[0]
                dt = current_time - last_update_time_production
                IntIntegralValueProduction += IntTotalValueProduction * dt / 3600
                last_update_time_production = current_time
        return IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production

    def calculate_consumption(item, result_type_meter, IntTotalValueConsumption, IntIntegralValueConsumption, last_update_time_consumption, current_time):
        if result_type_meter[0]["name"] == "Consumption meter":
            ArrayValueConsumption = [
                field["value"] for param in item.get("parameters", [])
                if param["name"] == "Basic" 
                for field in param.get("fields", [])
                if field["point_key"] == "ACActivePower"
            ]
            if ArrayValueConsumption and ArrayValueConsumption[0] is not None:
                IntTotalValueConsumption += ArrayValueConsumption[0]
                dt = current_time - last_update_time_consumption
                IntIntegralValueConsumption += IntTotalValueConsumption * dt / 3600
                last_update_time_consumption = current_time
        return IntTotalValueConsumption, IntIntegralValueConsumption, last_update_time_consumption

    def message_value_metter(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp):
        timeStampGetValueProductionAndConsumption = get_utc()
        gFloatValueMaxPredictProductionInstant_temp = 0
        ValueProductionAndConsumption = {
            "Timestamp": timeStampGetValueProductionAndConsumption,
            "instant": {},
        }
        if gArrayMessageAllDevice:
            for device in gArrayMessageAllDevice:
                if "mppt" in device:
                    for mppt in device["mppt"]:
                        if "power" in mppt:
                            gFloatValueMaxPredictProductionInstant_temp += mppt["power"]
        # instant power
        ValueProductionAndConsumption["instant"]["production"] = round(gIntValueProductionSystemp, 4)
        ValueProductionAndConsumption["instant"]["consumption"] = round(gIntValueConsumptionSystemp, 4)
        ValueProductionAndConsumption["instant"]["grid_feed"] = round((gIntValueProductionSystemp - gIntValueConsumptionSystemp), 4)
        ValueProductionAndConsumption["instant"]["max_production"] = round(gFloatValueMaxPredictProductionInstant_temp, 4)
        return ValueProductionAndConsumption

# ==================================================== Caculator PowerLit And ZeroExport  ==================================================================
class FuntionCaculatorPower:
    def __init__(self):
        pass

    async def calculate_system_performance(self, ModeSystemp, ValueSystemPerformance, ValueProductionSystemp, Setpoint):
        if ModeSystemp != 0:
            if Setpoint > 0 and ValueProductionSystemp > 0:
                ValueSystemPerformance = (ValueProductionSystemp / Setpoint) * 100
            elif Setpoint <= 0 and ValueProductionSystemp > 0:
                ValueSystemPerformance = 101
            else:
                ValueSystemPerformance = 0
        return ValueSystemPerformance

    def process_device_powerlimit_info(self, device):
        id_device = device["id_device"]
        mode = device["mode"]
        intPowerMaxOfInv = float(device["p_max"])
        return id_device, mode, intPowerMaxOfInv

    def calculate_power_value(self, intPowerMaxOfInv, modeSystem, TotalPowerInInvInManMode, TotalPowerInInvInAutoMode, Setpoint):
        # Tính toán hiệu suất cho thiết bị
        if modeSystem == 1:
            floatEfficiencySystemp = (Setpoint / TotalPowerInInvInAutoMode)
        else:
            floatEfficiencySystemp = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
        
        # Công suất của thiết bị bằng hiệu suất nhân với công suất tối đa.
        if 0 <= floatEfficiencySystemp <= 1:
            return floatEfficiencySystemp * intPowerMaxOfInv
        elif floatEfficiencySystemp < 0:
            return 0
        else:
            return intPowerMaxOfInv

    def create_control_item(self, device, PowerForEachInv, Setpoint, TotalPowerInInvInManMode, ValueProductionSystemp):
        id_device = device["id_device"]
        mode = device["mode"]
        ItemlistInvControlPowerLimitMode = {
            "id_device": id_device,
            "mode": mode,
            "time": get_utc(),
            "status": "power limit",
            "setpoint": Setpoint - TotalPowerInInvInManMode,
            "feedback": ValueProductionSystemp,
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

    async def calculate_setpoint(self, modeSystem, ValueConsump, ValueTotalPowerInInvInManMode,
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

        if not hasattr(self.calculate_setpoint, 'last_setpoint'):
            self.calculate_setpoint.last_setpoint = intAvgValueComsumtion
        
        new_setpoint = intAvgValueComsumtion
        setpointCalculatorPowerForEachInv = max(
            self.calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
            min(self.calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        self.calculate_setpoint.last_setpoint = setpointCalculatorPowerForEachInv
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump) / 100)
        if setpointCalculatorPowerForEachInv:
            setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv * ValueOffetConsump / 100
        return setpointCalculatorPowerForEachInv, ConsumptionAfterSudOfset