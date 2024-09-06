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
from utils.libMySQL import *
from utils.libTime import *
from dbService.projectSetup import ProjectSetupService

class ProjectSetup:
    def __init__(self):
        pass
    # Describe initializeValueControlAuto 
    # 	 * @description initializeValueControlAuto
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {}
    # 	 * @return return {
                #     "serial_number": serialNumber,
                #     "mode": ModeSystemp,
                #     "control_mode": gIntControlModeDetail,
                #     "value_offset_zero_export": OffsetZeroExport,
                #     "value_power_limit": PowerLimit,
                #     "value_offset_power_limit": OffsetPowerLimit,
                #     "threshold_zero_export": ThresholdZeroExport,
                #     "low_performance": LowPerformance,
                #     "high_performance": ArlamHighPerformance,
                # }
    # 	 */ 
    @staticmethod
    async def get_project_setup_values():
        OffsetZeroExport = 0
        PowerLimit = 0
        OffsetPowerLimit = 0
        ThresholdZeroExport = 0
        LowPerformance = 0
        ArlamHighPerformance = 0
        ModeSystemp = ""
        serialNumber = ""
        PowerLimit_temp = 0
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
                PowerLimit = (PowerLimit_temp - (PowerLimit_temp * OffsetPowerLimit) / 100) if OffsetPowerLimit is not None else PowerLimit_temp 
                ThresholdZeroExport = resultDB[0]["threshold_zero_export"]
                LowPerformance = resultDB[0]["low_performance"]
                ArlamHighPerformance = resultDB[0]["high_performance"]
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
            return None 
    # Describe pudFeedBackProjectSetup 
    # 	 * @description pudFeedBackProjectSetup
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service,topicFeedBack}
    # 	 * @return 
    # 	 */ 
    @staticmethod
    async def publish_project_setup(mqtt_service,topicFeedBack):
        try :
            db_new = await DBSessionManager.get_db()
            resultDB = await ProjectSetupService.selectAllProjectSetup(db_new)
            if resultDB:
                try:
                    OjectSentMQTT = resultDB[0]
                    OjectSentMQTT['mqtt'] = [
                        {"time_stamp": get_utc()},
                        {"status": 200}
                    ]
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
    # Describe insertInformationProjectSetup 
    # 	 * @description insertInformationProjectSetup
    # 	 * @author bnguyen
    # 	 * @since 2-05-2024
    # 	 * @param {mqtt_service, messageMQTT, topicFeedBack}
    # 	 * @return 
    # 	 */ 
    @staticmethod
    async def insert_project_setup_info(mqtt_service, messageMQTT, topicFeedBack):
        try:
            resultSet = messageMQTT.get('parameter', {})
            resultSet.pop('mqtt', None)
            token = messageMQTT.get('token', "")
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
                current_time = get_utc()
                data_send = {
                    "status": status,
                    "time_stamp": current_time,
                    "token": token,
                }
                MQTTService.push_data_zip(mqtt_service, topicFeedBack, data_send)
        except Exception as err:
            print(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")
    @staticmethod
    async def get_time_interval_logdevice():
        try :
            db_new = await DBSessionManager.get_db()
            resultDB = await ProjectSetupService.selectTimeLogInterval(db_new)
            if resultDB:
                try:
                    time = resultDB[0]
                    return time
                except Exception as err:
                    print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
        except Exception as err:
            print(f"Error MQTT subscribe get_time_interval_logdevice: '{err}'")
            return None 