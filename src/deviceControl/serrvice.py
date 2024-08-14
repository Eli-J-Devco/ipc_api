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
from deviceControl.cpu import cpu_service as cpu_init
from deviceControl.control import control_service as control_init
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                                mqtt_public_paho, mqtt_public_paho_zip,
                                mqttService)
from configs.config import orm_provider as db_config
from database.sql.device import all_query
from dataclasses import asdict, dataclass

from apiGateway.devices import devices_service
from apiGateway.project_setup import project_service
from apiGateway.rs485 import rs485_service
from apiGateway.template import template_service
from apiGateway.upload_channel import upload_channel_service

arr = sys.argv # Variables Array System
gStringModeSystempCurrent = ""
gFloatValueSystemPerformance = 0
# Parameters values PowerLimit and ZeroExport
gIntControlModeDetail = 0
gIntValueThresholdZeroExport = 0
gIntValueOffsetZeroExport = 0
gIntValuePowerLimit = 0
gIntValueOffsetPowerLimit = 0 
gListMovingAverageConsumption = collections.deque(maxlen=10)
gMaxValueChangeSetpoint = 10  # Maximum allowed change per second
# Performance Systemp 
gIntValueSettingArlamLowPerformance = 0
gIntValueSettingArlamHighPerformance = 0
# Parameters Value Production and Consumtion 
gIntValueProductionSystemp = 0
gIntValueConsumptionSystemp = 0
start_time_minutely = time.time()
# Parameters Value Power In Inv Each Mode 
gIntValueTotalPowerInInvInManMode = 0
gIntValueTotalPowerInInvInAutoMode = 0
gIntValueTotalPowerInALLInv = 0
# message device all 
gArrayMessageAllDevice = []
# Initialize a variable that stores previous information
net_io_counters_prev = {
    "TotalSent": 0,
    "TotalReceived": 0,
    "Timestamp": datetime.datetime.now()
}
disk_io_counters_prev = {
    "ReadBytes": 0,
    "WriteBytes": 0,
    "Timestamp": datetime.datetime.now()
}
# Infor Configuration
Mqtt_Broker = Config.MQTT_BROKER
Mqtt_Port = Config.MQTT_PORT
Mqtt_Topic = Config.MQTT_TOPIC +"/Dev/"
Mqtt_UserName = Config.MQTT_USERNAME
Mqtt_Password = Config.MQTT_PASSWORD
Topic_Control_Setup_Mode_Write = Config.MQTT_TOPIC_SUD_MODECONTROL_DEVICE
Topic_Control_Setup_Mode_Feedback = Config.MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL
Topic_Project_Information = Config.MQTT_TOPIC_PUD_PROJECT_SETUP
Topic_CPU_Information = Config.MQTT_TOPIC_PUD_CPU_SETUP
Topic_Project_Get = Config.MQTT_TOPIC_SUD_MODEGET_INFORMATION
Topic_CPU_Get = Config.MQTT_TOPIC_SUD_MODEGET_CPU
Topic_Control_Setup_Mode_Write_Detail = Config.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL
Topic_Control_Setup_Mode_Write_Detail_Feedback = Config.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK
Topic_Control_Setup_Auto = Config.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO
Topic_Control_Setup_Auto_Feedback = Config.MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
Topic_Devices_All = Config.MQTT_TOPIC_SUD_DEVICES_ALL
Topic_Control_Feedback = Config.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN
Topic_Control_FeedbackSetup = Config.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP
Topic_Control_WriteAuto = Config.MQTT_TOPIC_PUD_CONTROL_AUTO
Topic_Project_Set = Config.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE
Topic_Project_Set_Feedback = Config.MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE
Topic_Control_Process = Config.MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS
Topic_Meter_Monitor = Config.MQTT_TOPIC_PUD_MONIT_METER
Topic_Control_Alarm_Setting = Config.MQTT_TOPIC_SUD_SETTING_ARLAM
Topic_Control_Alarm_Feedback = Config.MQTT_TOPIC_PUD_SETTING_ARLAM_FEEDBACK
Topic_Control_Modify = Config.MQTT_TOPIC_SUD_MODIFY_DEVICE

def pathDirectory(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
path=pathDirectory("ipc_api") # name of project
sys.path.append(path)
from utils.logger_manager import LoggerSetup

arr = sys.argv
############################################################################ CPU ############################################################################
# Describe getCpuInformation 
# 	 * @description get cpu information
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return 
#      system_info = {
#     "Timestamp": timestamp,
#     "SystemInformation": {},
#     "BootTime": {},
#     "CPUInfo": {},
#     "MemoryInformation": {},
#     "DiskInformation": {},
#     "NetworkInformation": {}
#      }
# 	 */ 
async def PushData(StringSerialNumerInTableProjectSetup, topic, mqtt_service, host, port, username, password):
    # Tạo thông tin hệ thống cần gửi
    system_info = {
        "Timestamp": datetime.datetime.utcnow().isoformat(),
        "SystemInformation": {},  # Thêm thông tin hệ thống ở đây
        "BootTime": {},
        "CPUInfo": {},
        "MemoryInformation": {},
        "DiskInformation": {},
        "NetworkInformation": {}
    }
    # Lấy thông tin hệ thống (giả sử bạn có các hàm lấy thông tin)
    system_info["SystemInformation"] = cpu_init.getSystemInformation()
    system_info["CPUInfo"] = cpu_init.getCpuInformation()
    # Thêm các thông tin khác nếu cần
    try:
        # Gửi dữ liệu lên MQTT
        await MQTTService.push_data(mqtt_service,topic, system_info)
    except Exception as e:
        print(f"Error pushing data: {e}")
        
async def main():
    # Get Serial number From DB
    db_new = await db_config.get_db()
    project_init = project_service.ProjectService()
    results_project = await project_init.project_inform(db_new)

    if results_project is not None:
        StringSerialNumerInTableProjectSetup = results_project["serial_number"]
        mqtt_service = MQTTService(Mqtt_Broker, Mqtt_Port, Mqtt_UserName, Mqtt_Password, StringSerialNumerInTableProjectSetup)
        mqtt_service.set_topics(
            Topic_Control_Setup_Mode_Write,
            Topic_Project_Get,
            Topic_Control_Setup_Auto,
            Topic_Devices_All,
            Topic_CPU_Get,
            Topic_Project_Set,
            Topic_Control_Setup_Mode_Write_Detail,
            Topic_Control_Feedback,
            Topic_Control_Modify,
            Topic_Control_FeedbackSetup,
            Topic_Meter_Monitor,
            Topic_Control_Setup_Mode_Feedback,
            Topic_Control_Setup_Mode_Write,
            Topic_Control_Process,
            Topic_Control_Setup_Auto_Feedback,
            Topic_CPU_Information,
            Topic_Control_WriteAuto
        )
        # Start listening to the message
        await mqtt_service.start_mqtt_client()
        # Cycle
        scheduler = AsyncIOScheduler()
        scheduler.add_job(PushData, 'cron', second='*/1', args=[StringSerialNumerInTableProjectSetup,
                                                                    Topic_CPU_Information,
                                                                    mqtt_service,  # Truyền thể hiện mqtt_service
                                                                    Mqtt_Broker,
                                                                    Mqtt_Port,
                                                                    Mqtt_UserName,
                                                                    Mqtt_Password])
        scheduler.start()
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())