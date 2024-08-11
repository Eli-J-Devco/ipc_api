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
from getcpu import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)

async def calculate_system_performance_powerlimit(gStringModeSystempCurrent,gFloatValueSystemPerformance,gIntValueProductionSystemp,gIntValuePowerLimit):
    if gIntValuePowerLimit > 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = (gIntValueProductionSystemp / gIntValuePowerLimit) * 100
    elif gIntValuePowerLimit <= 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = 101
    else:
        gFloatValueSystemPerformance = 0
    return gFloatValueSystemPerformance
def process_device_powerlimit_info(device):
    id_device = device["id_device"]
    mode = device["mode"]
    intPowerMaxOfInv = float(device["p_max"])
    return id_device, mode, intPowerMaxOfInv
def calculate_power_value(intPowerMaxOfInv,gStringModeSystempCurrent,gIntValueTotalPowerInInvInManMode,gIntValueTotalPowerInInvInAutoMode,gIntValuePowerLimit):
    # Calulator peformance for device 
    if gStringModeSystempCurrent == 1:
        floatEfficiencySystemp = (gIntValuePowerLimit / gIntValueTotalPowerInInvInAutoMode)
    else:
        floatEfficiencySystemp = (gIntValuePowerLimit - gIntValueTotalPowerInInvInManMode) / gIntValueTotalPowerInInvInAutoMode
    # The power of the device is equal to the efficiency multiplied by the maximum power.
    if 0 <= floatEfficiencySystemp <= 1:
        return floatEfficiencySystemp * intPowerMaxOfInv
    elif floatEfficiencySystemp < 0:
        return 0
    else:
        return intPowerMaxOfInv
def create_control_item(device, gIntValuePowerForEachInvInModePowerLimit,gIntValuePowerLimit,gIntValueTotalPowerInInvInManMode,gIntValueProductionSystemp):
    id_device = device["id_device"]
    mode = device["mode"]
    ItemlistInvControlPowerLimitMode = {
        "id_device": id_device,
        "mode": mode,
        "time": get_utc(),
        "status": "power limit",
        "setpoint": gIntValuePowerLimit - gIntValueTotalPowerInInvInManMode,
        "feedback": gIntValueProductionSystemp,
        "parameter": []
    }
    # Create item for device
    if device['controlinv'] == 1:
        ItemlistInvControlPowerLimitMode["parameter"].append({"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModePowerLimit})
    elif device['controlinv'] == 0:
        ItemlistInvControlPowerLimitMode["parameter"].extend([
            {"id_pointkey": "ControlINV", "value": 1},
            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModePowerLimit}
        ])
    
    return ItemlistInvControlPowerLimitMode