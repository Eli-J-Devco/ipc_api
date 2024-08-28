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

# ============================================================== Mode Systemp ================================
class ModeSystemClass:
    def __init__(self):
        pass
    @staticmethod
    async def triggerDeviceModeChange(mqtt_service,topicFeedback):
        # Chuyển sang chế độ người dùng bao gồm cả chế độ thủ công và tự động
        try:
            db_new=await DBSessionManager.get_db()
            modes = await deviceListService.selectUniqueModesByDeviceType(db_new)
            if len(modes) == 1:
                if 0 in modes:
                    data_send = {"id_device": "Systemp", "mode": 0}
                elif 1 in modes:
                    data_send = {"id_device": "Systemp", "mode": 1}
            else:
                data_send = {"id_device": "Systemp", "mode": 2}
            
            MQTTService.push_data_zip(mqtt_service,topicFeedback, data_send)
        except asyncio.TimeoutError:
            print("Timeout waiting for data from MySQL")
    @staticmethod
    async def handleModeSystemChange(mqtt_service, messageMQTT, topicFeedback):
        db_new=await DBSessionManager.get_db()
        if messageMQTT.get('id_device') == 'Systemp':
            modeSysTemp = messageMQTT.get('mode')
            if modeSysTemp in [0, 1, 2]:
                updates = {
                        'mode': modeSysTemp,
                        # Thêm các trường khác nếu cần
                    }
                await ProjectSetupService.updateProjectSetup(db_new,updates)
            else:
                print("Failed to insert data")
            if modeSysTemp in [0, 1]:
                await deviceListService.updateDeviceModeByType(db_new, modeSysTemp)
            current_time = get_utc()
            objectSend = {
                "status": 200,
                "confirm_mode": modeSysTemp,
                "time_stamp": current_time,
            } if modeSysTemp in [0, 1, 2] else {
                "status": 400,
                "time_stamp": current_time,
            }
            MQTTService.push_data_zip(mqtt_service, topicFeedback, objectSend)
            return modeSysTemp
