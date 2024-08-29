# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import DBSessionManager
from utils.MQTTService import *
from utils.libTime import *
from dbService.projectSetup import ProjectSetupService
# ============================================================== Parametter Mode Detail Systemp ================================
class ModeDetailClass:
    def __init__(self):
        pass
    @staticmethod
    async def handleModeDetailChange(mqtt_service, messageMQTT, topicFeedback):
        # Biến cục bộ
        intComment = 0
        resultDB = []
        db_new=await DBSessionManager.get_db()
        # Nhận dữ liệu từ MQTT
        try:
            if messageMQTT and 'control_mode' in messageMQTT:
                ModeDetail = messageMQTT['control_mode'] 
                token = messageMQTT.get("token", "")
                updateModeDetail = {
                        'control_mode': ModeDetail,
                        # Thêm các trường khác nếu cần
                    }
                resultDB = await ProjectSetupService.updateProjectSetup(db_new,updateModeDetail)
                print("resultDB",resultDB)
                # Gửi phản hồi đến MQTT
                if resultDB is None:
                    intComment = 400 
                else:
                    intComment = 200 
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment, 
                    "token" : token
                }
                MQTTService.push_data_zip(mqtt_service, topicFeedback, objectSend)
                # Trả về biến toàn cục
                return ModeDetail
        except Exception as err:
            print(f"Error MQTT subscribe processUpdateModeControlDetail: '{err}'")
            return None  # Trả về None nếu có lỗi
    @staticmethod
    async def handleParametterDetailChange( mqtt_service, messageMQTT, topicFeedBack):
        ModeDetail = ""
        intComment = 0
        resultDBZeroExport = []
        resultDBPowerLimit = []
        db_new = await DBSessionManager.get_db()
        result = await ProjectSetupService.selectAllProjectSetup(db_new)
        try:
            if messageMQTT and 'mode' in messageMQTT and 'offset' in messageMQTT :
                ModeDetail = int(messageMQTT['mode'])
                token = messageMQTT.get("token", "")
                if ModeDetail == 1:
                    OffsetZeroExport, ThresholdZeroExport, resultDBZeroExport = await ModeDetailClass.handle_zero_export_mode(messageMQTT)
                    OffsetPowerLimit = result[0]["value_offset_power_limit"]
                    ValuePowerLimit = result[0]["value_power_limit"]
                elif ModeDetail == 2:
                    OffsetPowerLimit, ValuePowerLimit, resultDBPowerLimit = await ModeDetailClass.handle_power_limit_mode(messageMQTT)
                    OffsetZeroExport = result[0]["value_offset_zero_export"]
                    ThresholdZeroExport = result[0]["threshold_zero_export"]
                # Feedback to MQTT
                if ((resultDBZeroExport is None and ModeDetail == 1) or 
                    (resultDBPowerLimit is None and ModeDetail == 2) or 
                    ValuePowerLimit is None ):
                    intComment = 400 
                else:
                    intComment = 200 
                
                # Object Sent MQTT
                objectSend = {
                    "time_stamp": get_utc(),
                    "status": intComment,
                    "token":token
                }
                
                # Push MQTT
                MQTTService.push_data_zip(mqtt_service, topicFeedBack, objectSend)
                return {
                    "value_offset_zero_export": OffsetZeroExport,
                    "value_power_limit": ValuePowerLimit,
                    "value_offset_power_limit": OffsetPowerLimit,
                    "threshold_zero_export": ThresholdZeroExport,
                }
        except Exception as err:
            print(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'")
            return None
        
    async def handle_zero_export_mode( message):
        db_new = await DBSessionManager.get_db()
        ValueOffsetTemp = message.get("offset", 0)
        ValueThresholdTemp = message.get("threshold", 0)
        updateZeroExport = {
                'value_offset_zero_export': ValueOffsetTemp,
                'threshold_zero_export': ValueThresholdTemp,
                # Thêm các trường khác nếu cần
            }
        ResultQuery = await ProjectSetupService.updateProjectSetup(db_new,updateZeroExport)
        return ValueOffsetTemp, ValueThresholdTemp, ResultQuery

    async def handle_power_limit_mode( message):
        db_new = await DBSessionManager.get_db()
        ValueOffsetTemp = message.get("offset", 0)
        ValuePowerLimitTemp = message.get("value", 0)
        
        if ValuePowerLimitTemp is not None:
            ValuePowerLimit = ValuePowerLimitTemp - (ValuePowerLimitTemp * ValueOffsetTemp) / 100
            updatePowerLimit = {
                    'value_power_limit': ValuePowerLimitTemp,
                    'value_offset_power_limit': ValueOffsetTemp,
                    # Thêm các trường khác nếu cần
                }
            ResultQuery = await ProjectSetupService.updateProjectSetup(db_new,updatePowerLimit)
            return ValueOffsetTemp, ValuePowerLimit, ResultQuery
        
        return ValueOffsetTemp, None, None
