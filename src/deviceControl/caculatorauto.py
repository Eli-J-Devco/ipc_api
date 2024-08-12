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

async def calculate_system_performance(ModeSystemp,ValueSystemPerformance,ValueProductionSystemp,gIntValuePowerLimit):
    if ModeSystemp != 0 :
        if gIntValuePowerLimit > 0 and ValueProductionSystemp > 0:
            ValueSystemPerformance = (ValueProductionSystemp / gIntValuePowerLimit) * 100
        elif gIntValuePowerLimit <= 0 and ValueProductionSystemp > 0:
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

    if setpointCalculatorPowerForEachInv:
        setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv * ValueOffetConsump / 100
        ConsumptionAfterSudOfset = ValueConsump * ValueOffetConsump / 100
        print("ValueConsump",ValueConsump)
        print("ValueOffetConsump",ValueOffetConsump)
        print("ConsumptionAfterSudOfset",ConsumptionAfterSudOfset)
    return setpointCalculatorPowerForEachInv, ConsumptionAfterSudOfset