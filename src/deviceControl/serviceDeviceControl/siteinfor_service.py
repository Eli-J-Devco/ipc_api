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

class ProjectSetupClass:
    def __init__(self):
        pass
    @staticmethod
    async def initializeValueControlAuto():
        # Biến cục bộ
        OffsetZeroExport = 0
        PowerLimit = 0
        OffsetPowerLimit = 0
        ThresholdZeroExport = 0
        LowPerformance = 0
        ArlamHighPerformance = 0
        ModeSystemp = ""
        serialNumber = ""
        # Biến tạm
        PowerLimit_temp = 0
        # Lấy thông tin từ cơ sở dữ liệu lần đầu
        try:
            db_new=await DBSessionManager.get_db()
            resultDB = await ProjectSetupService.selectAllProjectSetup(db_new)
            if resultDB:
                serialNumber = resultDB[0]["serial_number"]
                ModeSystemp = resultDB[0]["mode"]
                gIntControlModeDetail = resultDB[0]["control_mode"]
                OffsetZeroExport = resultDB[0]["value_offset_zero_export"]
                PowerLimit_temp = resultDB[0]["value_power_limit"]
                OffsetPowerLimit = resultDB[0]["value_offset_power_limit"]
                PowerLimit = (PowerLimit_temp - (PowerLimit_temp * OffsetPowerLimit) / 100)
                ThresholdZeroExport = resultDB[0]["threshold_zero_export"]
                LowPerformance = resultDB[0]["low_performance"]
                ArlamHighPerformance = resultDB[0]["high_performance"]
                
                # Trả về các giá trị đã khởi tạo
                return {
                    "serial_number": serialNumber,
                    "mode": ModeSystemp,
                    "control_mode": gIntControlModeDetail,
                    "value_offset_zero_export": OffsetZeroExport,
                    "value_power_limit": PowerLimit,
                    "value_offset_power_limit": OffsetPowerLimit,
                    "threshold_zero_export": ThresholdZeroExport,
                    "low_performance": LowPerformance,
                    "high_performance": ArlamHighPerformance,
                }
        except Exception as err:
            print(f"Error MQTT subscribe initializeValueControlAuto: '{err}'")
            return None  # Trả về None nếu có lỗi
    @staticmethod
    async def pudFeedBackProjectSetup(mqtt_service,topicFeedBack):
        try :
            # Lấy thông tin từ cơ sở dữ liệu
            db_new = await DBSessionManager.get_db()
            resultDB = await ProjectSetupService.selectAllProjectSetup(db_new)
            if resultDB:
                try:
                    # Gửi thông tin đến MQTT
                    OjectSentMQTT = resultDB[0]
                    OjectSentMQTT['mqtt'] = [
                        {"time_stamp": get_utc()},
                        {"status": 200}
                    ]
                    print("OjectSentMQTT",OjectSentMQTT)
                    MQTTService.push_data_zip(mqtt_service,topicFeedBack, OjectSentMQTT)
                except Exception as err:
                    print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
        except Exception as err:
            data_send = {
                "mqtt": [
                        {"time_stamp" : get_utc()},
                        {"status":400}]
                        }
            MQTTService.push_data_zip(mqtt_service,topicFeedBack,data_send)
    @staticmethod
    async def insertInformationProjectSetup(mqtt_service, messageMQTT, topicFeedBack):
        try:
            # Tách thông tin mqtt từ thông tin được gửi
            resultSet = messageMQTT.get('parameter', {})
            resultSet.pop('mqtt', None)
            token = messageMQTT.get('token', "")
            # Lọc các kết quả nhận được để tạo truy vấn cập nhật thông tin cơ sở dữ liệu
            if resultSet:
                update_fields = ", ".join([f"{field} = %s" for field, value in resultSet.items()])
                update_values = [value for field, value in resultSet.items()]
                values = [tuple(update_values)]
                query = f"UPDATE project_setup SET {update_fields}"
                if query and update_values:
                    result = MySQL_Update_v2(query, values)
                if result is not None:
                    status = 200
                else:
                    status = 400
                # return of execution results to the end user
                current_time = get_utc()
                data_send = {
                    "status": status,
                    "time_stamp": current_time,
                    "token": token,
                }
                MQTTService.push_data_zip(mqtt_service, topicFeedBack, data_send)
        except Exception as err:
            print(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")