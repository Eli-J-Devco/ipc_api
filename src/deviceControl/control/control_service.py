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
async def processModeChange(gArrayMessageChangeModeSystemp, topicFeedbackModeSystemp, host, port, username, password):
    if gArrayMessageChangeModeSystemp.get('id_device') == 'Systemp':
        gStringModeSysTemp = gArrayMessageChangeModeSystemp.get('mode')
        if gStringModeSysTemp in [0, 1, 2]:
            await updateSystemMode(gStringModeSysTemp)
        else:
            print("Failed to insert data")
        if gStringModeSysTemp in [0, 1]:
            await updateDeviceMode(gStringModeSysTemp)
        current_time = get_utc()
        if gStringModeSysTemp in [0, 1, 2]:
            objectSend = {
                "status": 200,
                "confirm_mode": gStringModeSysTemp,
                "time_stamp": current_time,
            }
        else:
            objectSend = {
                "status": 400,
                "time_stamp": current_time,
            }
        # Push system_info to MQTT 
        mqtt_public_paho_zip(host, port, topicFeedbackModeSystemp, username, password, objectSend)
        return gStringModeSysTemp
async def updateSystemMode(mode):
    querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
    result = MySQL_Insert_v5(querysystemp, (mode,))
    return result

async def updateDeviceMode(mode):
    querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';"
    result = MySQL_Insert_v5(querydevice, (mode,))
    return result

async def handle_zero_export_mode(message):
    ResultQuery = None
    ValueOffset = None
    ValueThreshold = None
    if "offset" in message and "threshold" in message:
        # Get ValueOffset From Message
        ValueOffset = message.get("offset")
        # Get ValueThreshold From Message
        ValueThreshold = message.get("threshold")
        # Result Query 
        ResultQuery = MySQL_Update_V1("update project_setup set value_offset_zero_export = %s, threshold_zero_export = %s", (ValueOffset, ValueThreshold))
    return ValueOffset,ValueThreshold,ResultQuery

async def handle_power_limit_mode(message,TotalPower):
    ResultQuery = None
    ValueOffset = None
    ValuePowerLimit = None
    if "offset" in message and "value" in message:
        # Get ValueOffset From Message
        ValueOffset = message.get("offset")
        # Get ValuePowerLimit From Message
        ValuePowerLimitTemp = message.get("value")
        if ValuePowerLimitTemp is not None and ValuePowerLimitTemp <= TotalPower:
            if ValueOffset != None :
                ValuePowerLimit = ValuePowerLimitTemp - (ValuePowerLimitTemp * ValueOffset) / 100
            else:
                ValuePowerLimit = ValuePowerLimitTemp
            # Result Query 
            ResultQuery =  MySQL_Update_V1("update project_setup set value_power_limit = %s, value_offset_power_limit = %s", (ValuePowerLimitTemp, ValueOffset))
    return ValueOffset,ValuePowerLimit,ResultQuery
# ==================================================== Auto Device  ==================================================================
def extract_device_auto_info(item):
    if 'id_device' in item and 'mode' in item and 'status_device' in item:
        id_device = item['id_device']
        mode = item['mode']
        status_device = item['status_device']
        p_max = item['rated_power']
        p_max_custom = item.get('rated_power_custom')
        if p_max_custom is None:
            p_max_custom = p_max
        p_min_percent = item['min_watt_in_percent']
        p_min = (p_max * p_min_percent) / 100 if p_max and p_min_percent else 0
        value = get_device_value(item, "ControlINV")
        if value is None:
            return None
        operator = get_device_value(item, "OperatingState")
        if operator is None:
            return None
        slope = get_device_value(item, "WMax", field_key='slope')
        if slope is None:
            return None
        results_device_type = item.get('name_device_type') 
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
# ==================================================== All Device  ==================================================================
def extract_device_all_info(item):
    if 'id_device' in item and 'mode' in item and 'status_device' in item:
        id_device = item['id_device']
        mode = item['mode']
        status_device = item['status_device']
        p_max = item['rated_power']
        p_max_custom = item.get('rated_power_custom')
        if p_max_custom is None:
            p_max_custom = p_max
        p_min_percent = item['min_watt_in_percent']
        device_name = item['device_name']
        results_device_type = item['name_device_type']
        # Check Device Is INV
        if results_device_type == "PV System Inverter":
            operator, wmax, capacity_power, real_power = get_device_parameters(item)
            # Check Device Offline Or Online
            if status_device == 'offline':
                real_power = 0.0
                operator = "off"
            # Calculator Pmin
            p_min = calculate_p_min(p_max_custom, p_min_percent)
            # Returns Information INV 
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

def get_device_parameters(item):
    stringOperatorText = {
        0: "shutting down",
        1: "shutting down",
        4: "running",
        5: "running",
        6: "shutting down",
        7: "fault",
    }
    # Get Operator Each Of Device From Message All 
    ArrayOperator = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
    intOperator = ArrayOperator[0] if ArrayOperator else 0
    operator = stringOperatorText.get(intOperator, "off")
    # Get Wmax , Capacity Power , Real Power Each Of Device From Message All
    wmax = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "WMax"), 0)
    capacity_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "PowerOutputCapability"), 0)
    real_power = next((field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"), 0)
    # Return Wmax , Capacity Power , Real Power
    return operator, wmax, capacity_power, real_power

def calculate_total_wmax(device_list,power_auto):
    total_power_write_inv = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None), 2)
    total_power_manual = round(sum(device['wmax'] for device in device_list if device['wmax'] is not None and device['mode'] == 0), 2)
    total_power = round((total_power_manual + power_auto),2)
    return total_power, total_power_manual

def calculate_p_min(p_max_custom, p_min_percent):
    return round((p_max_custom * p_min_percent) / 100, 4) if p_max_custom and p_min_percent else 0.0

def update_system_performance(current_mode,systemPerformance, total_power_in_all_inv, production_system, low_performance_threshold, high_performance_threshold):
    # Calculate system performance
    if current_mode == 0:
        systemPerformance = (production_system / total_power_in_all_inv) * 100 if total_power_in_all_inv else 0
    # Round performance to 1 decimal place
    systemPerformance = round(systemPerformance, 1)
    # Determine performance status
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
# ==================================================== Meter ==================================================================
def get_device_type(id_device):
    return MySQL_Select("SELECT `device_type`.`name` FROM `device_type` INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id WHERE `device_list`.id = %s", (id_device,))

def calculate_production(item, result_type_meter, IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production, current_time):
    if result_type_meter[0]["name"] == "PV System Inverter": 
        ArrayValueProduction = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
        if ArrayValueProduction and ArrayValueProduction[0] is not None:
            IntTotalValueProduction += ArrayValueProduction[0]
            dt = current_time - last_update_time_production
            IntIntegralValueProduction += IntTotalValueProduction * dt / 3600
            last_update_time_production = current_time
    return IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production

def calculate_consumption(item, result_type_meter, IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption, current_time):
    if result_type_meter[0]["name"] == "Consumption meter":
        ArrayValueConsumtion = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
        if ArrayValueConsumtion and ArrayValueConsumtion[0] is not None:
            IntTotalValueConsumtion += ArrayValueConsumtion[0]
            dt = current_time - last_update_time_comsumption
            IntIntegralValueConsumtion += IntTotalValueConsumtion * dt / 3600 
            last_update_time_comsumption = current_time
    return IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption

def messageSentMQTT(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp):
    timeStampGetValueProductionAndConsumtion = get_utc()
    gFloatValueMaxPredictProductionInstant_temp = 0
    ValueProductionAndConsumtion = {
        "Timestamp": timeStampGetValueProductionAndConsumtion,
        "instant": {},
    }
    if gArrayMessageAllDevice:
        for device in gArrayMessageAllDevice:
            if "mppt" in device:
                for mppt in device["mppt"]:
                    if "power" in mppt:
                        gFloatValueMaxPredictProductionInstant_temp += mppt["power"]
    # instant power
    ValueProductionAndConsumtion["instant"]["production"] = round(gIntValueProductionSystemp, 4)
    ValueProductionAndConsumtion["instant"]["consumption"] = round(gIntValueConsumptionSystemp, 4)
    ValueProductionAndConsumtion["instant"]["grid_feed"] = round((gIntValueProductionSystemp - gIntValueConsumptionSystemp), 4)
    ValueProductionAndConsumtion["instant"]["max_production"] = round(gFloatValueMaxPredictProductionInstant_temp, 4)
    return ValueProductionAndConsumtion
# ==================================================== Caculator ==================================================================
async def calculate_system_performance(ModeSystemp,ValueSystemPerformance,ValueProductionSystemp,Setpoint):
    if ModeSystemp != 0 :
        if Setpoint > 0 and ValueProductionSystemp > 0:
            ValueSystemPerformance = (ValueProductionSystemp / Setpoint) * 100
        elif Setpoint <= 0 and ValueProductionSystemp > 0:
            ValueSystemPerformance = 101
        else:
            ValueSystemPerformance = 0
        return ValueSystemPerformance
def process_device_powerlimit_info(device):
    id_device = device["id_device"]
    mode = device["mode"]
    intPowerMaxOfInv = float(device["p_max"])
    return id_device, mode, intPowerMaxOfInv
def calculate_power_value(intPowerMaxOfInv,modeSystem,TotalPowerInInvInManMode,TotalPowerInInvInAutoMode,Setpoint):
    # Calulator peformance for device 
    if modeSystem == 1:
        floatEfficiencySystemp = (Setpoint / TotalPowerInInvInAutoMode)
    else:
        floatEfficiencySystemp = (Setpoint - TotalPowerInInvInManMode) / TotalPowerInInvInAutoMode
    # The power of the device is equal to the efficiency multiplied by the maximum power.
    if 0 <= floatEfficiencySystemp <= 1:
        return floatEfficiencySystemp * intPowerMaxOfInv
    elif floatEfficiencySystemp < 0:
        return 0
    else:
        return intPowerMaxOfInv
def create_control_item(device, PowerForEachInv,Setpoint,TotalPowerInInvInManMode,ValueProductionSystemp):
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
    # Create item for device
    if device['controlinv'] == 1:
        ItemlistInvControlPowerLimitMode["parameter"].append({"id_pointkey": "WMax", "value": PowerForEachInv})
    elif device['controlinv'] == 0:
        ItemlistInvControlPowerLimitMode["parameter"].extend([
            {"id_pointkey": "ControlINV", "value": 1},
            {"id_pointkey": "WMax", "value": PowerForEachInv}
        ])
    
    return ItemlistInvControlPowerLimitMode
async def calculate_setpoint(modeSystem ,ValueConsump,ValueTotalPowerInInvInManMode,gListMovingAverageConsumption,\
    gMaxValueChangeSetpoint,ValueOffetConsump):
    ConsumptionAfterSudOfset = 0.0
    if modeSystem == 1:
        gListMovingAverageConsumption.append(ValueConsump)
    else:
        gListMovingAverageConsumption.append(ValueConsump - ValueTotalPowerInInvInManMode)
    if ValueConsump > ValueTotalPowerInInvInManMode:
        intAvgValueComsumtion = sum(gListMovingAverageConsumption) / len(gListMovingAverageConsumption)
    else:
        intAvgValueComsumtion = 0
    if not hasattr(calculate_setpoint, 'last_setpoint'):
        calculate_setpoint.last_setpoint = intAvgValueComsumtion
    new_setpoint = intAvgValueComsumtion
    setpointCalculatorPowerForEachInv = max(
        calculate_setpoint.last_setpoint - gMaxValueChangeSetpoint,
        min(calculate_setpoint.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
    )
    calculate_setpoint.last_setpoint = setpointCalculatorPowerForEachInv
    if ValueOffetConsump != None and setpointCalculatorPowerForEachInv:
        ConsumptionAfterSudOfset = ValueConsump * ((100 - ValueOffetConsump)/ 100)
        setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv * ValueOffetConsump / 100
    else:
        ConsumptionAfterSudOfset = ValueConsump
        setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv 
    return setpointCalculatorPowerForEachInv, ConsumptionAfterSudOfset