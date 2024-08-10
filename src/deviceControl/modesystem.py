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

async def processModeChange(gArrayMessageChangeModeSystemp, topicFeedbackModeSystemp, host, port, username, password):
    if gArrayMessageChangeModeSystemp.get('id_device') == 'Systemp':
        gStringModeSysTemp = gArrayMessageChangeModeSystemp.get('mode')
        if gStringModeSysTemp in [0, 1, 2]:
            print("1111111")
            await updateDatabase(gStringModeSysTemp)
        else:
            print("Failed to insert data")
        print("222222")
        if gStringModeSysTemp in [0, 1]:
            await updateDeviceMode(gStringModeSysTemp)
        print("33333333")
        current_time = get_utc()
        if gStringModeSysTemp in [0, 1, 2]:
            objectSend = {
                "status": 200,
                "confirm_mode": gStringModeSysTemp,
                "time_stamp": current_time,
            }
            print("44444444")
        else:
            objectSend = {
                "status": 400,
                "time_stamp": current_time,
            }
        # Push system_info to MQTT 
        mqtt_public_paho_zip(host, port, topicFeedbackModeSystemp, username, password, objectSend)
        print("gStringModeSysTemp",gStringModeSysTemp)
        return gStringModeSysTemp
async def updateDatabase(mode):
    querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
    result = await MySQL_Insert_v5(querysystemp, (mode,))
    return result

async def updateDeviceMode(mode):
    querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';"
    result = await MySQL_Insert_v5(querydevice, (mode,))
    return result