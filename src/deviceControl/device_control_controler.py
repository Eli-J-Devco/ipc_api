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
import cpu.cpu_service as cpu_init
import control.control_service as control_init
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
async def getIPCHardwareInformation(StringSerialNumerInTableProjectSetup, Topic_CPU_Information, host, port, username, password):
    global net_io_counters_prev, disk_io_counters_prev
    topicPublicInformationCpu = StringSerialNumerInTableProjectSetup + Topic_CPU_Information
    timeStampPudCpuInformation = get_utc()
    system_info = {
        "Timestamp": timeStampPudCpuInformation,
        "Time": int(time.time() * 1000),
        "SystemInformation": {},
        "BootTime": {},
        "CPUInfo": {},
        "MemoryInformation": {},
        "DiskInformation": {},
        "NetworkInformation": {},
        "NetworkSpeed": {},
        "DiskIO": {}
    }
    try:
        # Get system information
        system_info["SystemInformation"] = cpu_init.getSystemInformation()
        system_info["BootTime"] = cpu_init.getBootTime() or {}
        system_info["CPUInfo"] = cpu_init.getCpuInformation() or {}
        system_info["MemoryInformation"] = cpu_init.getMemoryInformation() or {}
        system_info["DiskInformation"] = cpu_init.getDiskInformation() or {}
        system_info["NetworkInformation"] = cpu_init.getNetworkInformation() or {}
        system_info["NetworkSpeed"] = cpu_init.getNetworkSpeedInformation(net_io_counters_prev) or {}
        system_info["DiskIO"] = cpu_init.getDiskIoInformation(disk_io_counters_prev) or {}
        # Check that all fields are not None
        if all(system_info.values()):
            # Push system_info to MQTT 
            mqtt_public_paho_zip(host, port, topicPublicInformationCpu, username, password, system_info)
    except Exception as err:
        print(f"Error MQTT subscribe getCpuInformation: '{err}'")
############################################################################ Mode Systemp ############################################################################
# Describe subSystempModeWhenUserChangeModeSystemp 
# 	 * @description subSystempModeWhenUserChangeModeSystemp
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {result_topic1,ModeSysTemp}
# 	 * @return ModeSysTemp
# 	 */ 
async def subSystempModeWhenUserChangeModeSystemp(gArrayMessageChangeModeSystemp, StringSerialNumerInTableProjectSetup, Topic_Control_Setup_Mode_Feedback, host, port, username, password):
    # Global variables
    global gStringModeSystempCurrent
    topicFeedbackModeSystemp = StringSerialNumerInTableProjectSetup + Topic_Control_Setup_Mode_Feedback
    try:
        if gArrayMessageChangeModeSystemp:
            gStringModeSystempCurrent = await control_init.processModeChange(gArrayMessageChangeModeSystemp, topicFeedbackModeSystemp, host, port, username, password)
    except Exception as err:
        print(f"Error MQTT subscribe subSystempModeWhenUserChangeModeSystemp: '{err}'")
# Describe pudSystempModeTrigerEachDeviceChange
# /**
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 02-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup,host, port, username, password}
# 	 * @return push message systemp when user changes mode each device
# 	 */
async def pudSystempModeTrigerEachDeviceChange(MessageCheckModeSystemp, StringSerialNumerInTableProjectSetup,Topic_Control_Setup_Mode_Write,\
    host, port, username, password):
    # Local variables
    topicpud = StringSerialNumerInTableProjectSetup + Topic_Control_Setup_Mode_Write
    # Switch to user mode that is both man and auto
    if MessageCheckModeSystemp:
        try:
            result_checkmode_control = await MySQL_Select_v1("SELECT device_list.mode ,device_list.id FROM device_list JOIN device_type ON device_list.id_device_type = device_type.id WHERE device_type.name = 'PV System Inverter' AND device_list.status = 1;")
            modes = set([item['mode'] for item in result_checkmode_control])
            if len(modes) == 1:
                if 0 in modes:
                    data_send = {"id_device": "Systemp", "mode": 0}
                elif 1 in modes:
                    data_send = {"id_device": "Systemp", "mode": 1}
            else:
                data_send = {"id_device": "Systemp", "mode": 2}
            mqtt_public_paho_zip(host, port, topicpud, username, password, data_send)
        except asyncio.TimeoutError:
            print("Timeout waiting for data from MySQL")
############################################################################ Config SiteInfo ############################################################################
# Describe pudFeedBackProjectSetup 
# 	 * @description pudFeedBackProjectSetup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {host, port, topicPublic, username, password}
# 	 * @return data_send
# 	 */ 
async def pudFeedBackProjectSetup(host, port, topicPublic, username, password):
    queryAllTableProjectSetup = "SELECT * FROM `project_setup`"
    # Get information from database
    resultAllInformationTableProjectSetup = await MySQL_Select_v1(queryAllTableProjectSetup)
    if resultAllInformationTableProjectSetup:
        try:
    # Sent information to Mqtt
            dataSendTopicProjectInformation = resultAllInformationTableProjectSetup[0]
            dataSendTopicProjectInformation['mqtt'] = [
                {"time_stamp": get_utc()},
                {"status": 200}
            ]
            mqtt_public_paho_zip(host, port, topicPublic, username, password, dataSendTopicProjectInformation )
        except Exception as err:
            print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
# Describe insertInformationProjectSetup 
# 	 * @description insertInformationProjectSetup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result, host, port, topicPublic, username, password}
# 	 * @return data_send
# 	 */ 
async def insertInformationProjectSetup(messageInsertInformationProjectSetup, host, port, topicPublicInformationProjectSetup, username, password):
    try:
        # separate mqtt information on sent infromation
        resultSet = messageInsertInformationProjectSetup.get('parameter', {})
        resultSet.pop('mqtt', None)
        # Filter the received results to create a query to update database information
        if resultSet:
            update_fields = ", ".join([f"{field} = %s" for field, value in resultSet.items()])
            update_values = [value for field, value in resultSet.items()]
            values = [tuple(update_values)]
            query = f"UPDATE project_setup SET {update_fields}"
            if query and values:
                result = MySQL_Update_v2(query, values)
                if result is not None:
                    status = 200
                else:
                    status = 400
                # return of execution results to the end user
                current_time = get_utc()
                data_send = {
                    "status": status,
                    "time_stamp": current_time
                }
                mqtt_public_paho_zip(host, port, topicPublicInformationProjectSetup, username, password, data_send)
        else:
            current_time = get_utc()
            data_send = {
                "status": 200,
                "time_stamp": current_time
            }
            mqtt_public_paho_zip(host, port, topicPublicInformationProjectSetup, username, password, data_send)
    except Exception as err:
        print(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")
# Describe pudInformationProjectSetupWhenRequest 
# 	 * @description pudInformationProjectSetupWhenRequest
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result ,StringSerialNumerInTableProjectSetup,host, port, username, password}
# 	 * @return call pudFeedBackProjectSetup
# 	 */ 
async def pudInformationProjectSetupWhenRequest(messageGetInformation ,StringSerialNumerInTableProjectSetup,host, port, username, password):
    global Topic_Project_Information
    topicPudAllInformationTableProjectSetup = StringSerialNumerInTableProjectSetup + Topic_Project_Information
    timeStampPudInformationProjectSetup = get_utc()
    try:
        if messageGetInformation and 'get_information' in messageGetInformation:
            await pudFeedBackProjectSetup(host,
                                            port,
                                            topicPudAllInformationTableProjectSetup,
                                            username,
                                            password)                       
    except Exception as err:
        data_send = {
            "mqtt": [
                    {"time_stamp" : timeStampPudInformationProjectSetup},
                    {"status":400}]
                    }
        mqtt_public_paho_zip(host, port, topicPudAllInformationTableProjectSetup, username, password, data_send)
# Describe insertInformationProjectSetupWhenRequest 
# 	 * @description insertInformationProjectSetupWhenRequest
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result ,StringSerialNumerInTableProjectSetup,host, port, username, password}
# 	 * @return call insertInformationProjectSetup
# 	 */ 
async def insertInformationProjectSetupWhenRequest(messageInsertInformationProjectSetup ,StringSerialNumerInTableProjectSetup,host, port, username, password):
    global Topic_Project_Set_Feedback
    topicPudInsertInformationProjectSetupWhenRequest = StringSerialNumerInTableProjectSetup + Topic_Project_Set_Feedback
    try:
        if messageInsertInformationProjectSetup and 'set_information' in messageInsertInformationProjectSetup:
            await insertInformationProjectSetup(messageInsertInformationProjectSetup,
                                            host,
                                            port,
                                            topicPudInsertInformationProjectSetupWhenRequest,
                                            username,
                                            password)     
            await initializeValueControlAuto()
        else:
            pass
    except Exception as err:
        print(f"Error MQTT subscribe insertInformationProjectSetupWhenRequest: '{err}'") 
# Describe getListDeviceAutoModeInALLInv 
# 	 * @description getListDeviceAutoModeInALLInv
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
############################################################################ List Device Auto ############################################################################
async def getListDeviceAutoModeInALLInv(messageAllDevice):
    global gIntValueTotalPowerInInvInAutoMode
    ArayyDeviceList = []
    if messageAllDevice and isinstance(messageAllDevice, list):
        for item in messageAllDevice:
            device_info = control_init.extract_device_auto_info(item)
            if not device_info:
                continue
            # Get Information Each Device 
            id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type = device_info
            # Check Device Auto 
            if control_init.is_device_controlable(results_device_type, status_device, mode, operator):
                ArayyDeviceList.append({
                    'id_device': id_device,
                    'mode': mode,
                    'status_device': status_device,
                    'p_max': p_max_custom,
                    'p_min': p_min,
                    'controlinv': value,
                    'operator': operator,
                    'slope': slope,
                })
    # Caculator Power Device In Auto Mode
    gIntValueTotalPowerInInvInAutoMode = round(sum(device['p_max'] for device in ArayyDeviceList if device['p_max'] is not None),2)
    return ArayyDeviceList
############################################################################ List Device Systemp ############################################################################
# Describe getListALLInvInProject 
# 	 * @description getListALLInvInProject
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
async def getListALLInvInProject(messageAllDevice, StringSerialNumerInTableProjectSetup,Topic_Control_Process, host, port, username, password):
    global gIntValueProductionSystemp, gIntValueSettingArlamLowPerformance,gIntValueSettingArlamHighPerformance,\
        gIntValueTotalPowerInALLInv,gStringModeSystempCurrent,gIntValueTotalPowerInInvInManMode,gIntValueTotalPowerInInvInAutoMode,gFloatValueSystemPerformance
    ArrayDeviceList = []
    # Get Informatio about the device
    if messageAllDevice and isinstance(messageAllDevice, list):
        for item in messageAllDevice:
            device_info = control_init.extract_device_all_info(item)
            if device_info:
                ArrayDeviceList.append(device_info)
    # Calculate the sum of wmax values ​​of all inv in the system
    gIntValueTotalPowerInALLInv,gIntValueTotalPowerInInvInManMode = control_init.calculate_total_wmax(ArrayDeviceList,gIntValueTotalPowerInInvInAutoMode)
    # Call the update_system_performance function and get the return value
    gFloatValueSystemPerformance, StringMessageStatusSystemPerformance, intStatusSystemPerformance = control_init.update_system_performance(
        gStringModeSystempCurrent,
        gFloatValueSystemPerformance,
        gIntValueTotalPowerInALLInv,
        gIntValueProductionSystemp,
        gIntValueSettingArlamLowPerformance,
        gIntValueSettingArlamHighPerformance
    )
    # Message Public MQTT
    result = {
        "ModeSystempCurrent": gStringModeSystempCurrent,
        "devices": ArrayDeviceList,
        "total_max_power": gIntValueTotalPowerInALLInv,
        "total_max_power_man": gIntValueTotalPowerInInvInManMode,
        "total_max_power_auto": gIntValueTotalPowerInInvInAutoMode,
        "system_performance": {
            "performance": gFloatValueSystemPerformance,
            "message": StringMessageStatusSystemPerformance,
            "status": intStatusSystemPerformance
        }
    }
    # Public MQTT
    mqtt_public_paho_zip(host, port, StringSerialNumerInTableProjectSetup + Topic_Control_Process, username, password, result)
    push_data_to_mqtt(host, port, StringSerialNumerInTableProjectSetup + Topic_Control_Process + "Binh", username, password, result)
    return ArrayDeviceList
# Describe getValueProductionAndConsumtion 
# 	 * @description getValueProductionAndConsumtion
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return value_production ,value_consumption
# 	 */ 
############################################################################ Get Value Metter ############################################################################
async def getValueProductionAndConsumtion(gArrayMessageAllDevice, StringSerialNumerInTableProjectSetup, Topic_Meter_Monitor, host, port, username, password):
    global gIntValueProductionSystemp, gIntValueConsumptionSystemp,start_time_minutely
    # Local variables
    current_time = time.time()
    IntTotalValueProduction, IntTotalValueConsumtion = 0, 0
    IntIntegralValueProduction, IntIntegralValueConsumtion = 0, 0
    last_update_time_comsumption = start_time_minutely
    last_update_time_production = start_time_minutely
    # Get Value Production And Consumtion From message All
    if gArrayMessageAllDevice:
        for item in gArrayMessageAllDevice:
            if 'id_device' in item:
                id_device = item['id_device']
                result_type_meter = control_init.get_device_type(id_device)
                if result_type_meter:
                    IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production = control_init.calculate_production(item, result_type_meter, IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production, current_time)
                    IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption = control_init.calculate_consumption(item, result_type_meter, IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption, current_time)
        # Update the global values ​​of total production and total consumption
        gIntValueProductionSystemp = IntTotalValueProduction
        gIntValueConsumptionSystemp = IntTotalValueConsumtion
    try:
        ValueProductionAndConsumtion = control_init.messageSentMQTT(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp)
        # Push system_info to MQTT
        mqtt_public_paho_zip(host, port, StringSerialNumerInTableProjectSetup + Topic_Meter_Monitor, username, password, ValueProductionAndConsumtion)
        push_data_to_mqtt(host, port, StringSerialNumerInTableProjectSetup + Topic_Meter_Monitor + "Binh", username, password, ValueProductionAndConsumtion)
    except Exception as err:
        print(f"Error MQTT subscribe pudValueProductionAndConsumtionInMQTT: '{err}'")
############################################################################ Power Limit Control  ############################################################################
# Describe processCaculatorPowerForInvInPowerLimitMode 
# 	 * @description processCaculatorPowerForInvInPowerLimitMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return gIntValuePowerForEachInvInModePowerLimit
# 	 */ 
async def processCaculatorPowerForInvInPowerLimitMode(StringSerialNumerInTableProjectSetup,Topic_Control_WriteAuto, host, port, username, password):
    global gArrayMessageAllDevice, gIntValuePowerLimit, gIntValueProductionSystemp, gIntValueTotalPowerInInvInAutoMode,\
    gStringModeSystempCurrent, gFloatValueSystemPerformance,gIntValueTotalPowerInInvInManMode , gIntControlModeDetail
    # Local variables
    gArraydevices = []
    gIntValuePowerForEachInvInModePowerLimit = 0 
    processCaculatorPowerForInvInPowerLimitMode = StringSerialNumerInTableProjectSetup + Topic_Control_WriteAuto
    if gIntValuePowerLimit != None :
        ValuePowerLimitCaculator = gIntValuePowerLimit
    else:
        ValuePowerLimitCaculator = 0.0
    # Get List Device Can Control 
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
    # Caculator System Performance 
    if gStringModeSystempCurrent != 0:
        gFloatValueSystemPerformance = await control_init.calculate_system_performance(gStringModeSystempCurrent,gFloatValueSystemPerformance,\
        gIntValueProductionSystemp,ValuePowerLimitCaculator)
    # Get Infor Device Control 
    if gArraydevices:
        listInvControlPowerLimitMode = []
        for device in gArraydevices:
            id_device, mode, intPowerMaxOfInv = control_init.process_device_powerlimit_info(device)
            gIntValuePowerForEachInvInModePowerLimit = control_init.calculate_power_value(intPowerMaxOfInv,gStringModeSystempCurrent,gIntValueTotalPowerInInvInManMode,\
                gIntValueTotalPowerInInvInAutoMode,ValuePowerLimitCaculator)
            # Create Infor Device Publish MQTT
            if gIntValueProductionSystemp < ValuePowerLimitCaculator:
                item = control_init.create_control_item(gIntControlModeDetail,device, gIntValuePowerForEachInvInModePowerLimit,ValuePowerLimitCaculator,\
                    gIntValueTotalPowerInInvInManMode,gIntValueProductionSystemp)
            else:
                item = {
                    "id_device": id_device,
                    "mode": mode,
                    "status": "power limit",
                    "setpoint": ValuePowerLimitCaculator - gIntValueTotalPowerInInvInManMode,
                    "feedback": gIntValueProductionSystemp,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": max(0, gIntValuePowerForEachInvInModePowerLimit - (gIntValueProductionSystemp - ValuePowerLimitCaculator))}
                    ]
                }
            # Create List Device 
            listInvControlPowerLimitMode.append(item)
        # Push MQTT
        if len(gArraydevices) == len(listInvControlPowerLimitMode):
            mqtt_public_paho_zip(host, port, processCaculatorPowerForInvInPowerLimitMode, username, password, listInvControlPowerLimitMode)
            push_data_to_mqtt(host, port, processCaculatorPowerForInvInPowerLimitMode + "Binh", username, password, listInvControlPowerLimitMode)
############################################################################ Zero Export Control ############################################################################
# Describe processCaculatorPowerForInvInZeroExportMode 
# 	 * @description processCaculatorPowerForInvInZeroExportMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return gIntValuePowerForEachInvInModeZeroExport
# 	 */ 
async def processCaculatorPowerForInvInZeroExportMode(StringSerialNumerInTableProjectSetup,Topic_Control_WriteAuto, host, port, username, password):
    global gArrayMessageAllDevice, gIntValueThresholdZeroExport, gIntValueOffsetZeroExport, gIntValueConsumptionSystemp,\
        gIntValueProductionSystemp, gIntValueTotalPowerInInvInAutoMode,gListMovingAverageConsumption, gIntValueTotalPowerInInvInManMode, \
        gStringModeSystempCurrent, gFloatValueSystemPerformance , gIntControlModeDetail
    # Local variables
    gArraydevices = []
    topicPudCaculatorPowerForInvInZeroExportMode = StringSerialNumerInTableProjectSetup + Topic_Control_WriteAuto
    gIntValuePowerForEachInvInModeZeroExport = 0
    intPracticalConsumptionValue = 0.0
    setpointCalculatorPowerForEachInv = 0 
    if gIntValueThresholdZeroExport != None :
        ValueThresholdZeroExportCaculator = gIntValueThresholdZeroExport
    else:
        ValueThresholdZeroExportCaculator = 0.0
    # Get Setpoint ,Value Consumption System 
    if gIntValueConsumptionSystemp:
        setpointCalculatorPowerForEachInv, intPracticalConsumptionValue = await control_init.calculate_setpoint(gStringModeSystempCurrent,gIntValueConsumptionSystemp,gIntValueTotalPowerInInvInManMode,\
        gListMovingAverageConsumption,gMaxValueChangeSetpoint,gIntValueOffsetZeroExport)
    # Get List Device Can Control 
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
    # Caculator System Performance 
    if gStringModeSystempCurrent != 0:
        gFloatValueSystemPerformance = await control_init.calculate_system_performance(gStringModeSystempCurrent,gFloatValueSystemPerformance,\
        gIntValueProductionSystemp,intPracticalConsumptionValue)
    if gArraydevices:
        listInvControlZeroExportMode = []
        for device in gArraydevices:
            id_device, mode, intPowerMaxOfInv = control_init.process_device_powerlimit_info(device)
            gIntValuePowerForEachInvInModeZeroExport = control_init.calculate_power_value(intPowerMaxOfInv, gStringModeSystempCurrent, 
                gIntValueTotalPowerInInvInManMode, gIntValueTotalPowerInInvInAutoMode, setpointCalculatorPowerForEachInv)
            # Create Infor Device Publish MQTT
            if gIntValueProductionSystemp < intPracticalConsumptionValue and \
                gIntValueConsumptionSystemp >= ValueThresholdZeroExportCaculator and gIntValueConsumptionSystemp >= 0:
                item = control_init.create_control_item(gIntControlModeDetail,device, gIntValuePowerForEachInvInModeZeroExport,setpointCalculatorPowerForEachInv,\
                gIntValueTotalPowerInInvInManMode,gIntValueProductionSystemp)
            else:
                item = {
                    "id_device": id_device,
                    "mode": mode,
                    "status": "zero export",
                    "setpoint": setpointCalculatorPowerForEachInv,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": 0}
                    ]
                }
            # Create List Device 
            listInvControlZeroExportMode.append(item)
        # Push MQTT
        if len(gArraydevices) == len(listInvControlZeroExportMode):
            mqtt_public_paho_zip(host, port, topicPudCaculatorPowerForInvInZeroExportMode, username, password, listInvControlZeroExportMode)
            push_data_to_mqtt(host, port, topicPudCaculatorPowerForInvInZeroExportMode + "Binh", username, password, listInvControlZeroExportMode)
############################################################################ Setup Parameter Control ############################################################################
# Describe processUpdateParameterModeDetail 
# 	 * @description processUpdateParameterModeDetail
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup, host ,port ,username ,password}
# 	 * @return MySQL_Update gIntValueOffsetZeroExport,gIntValuePowerLimit,gIntValueOffsetPowerLimit
# 	 */ 
async def processUpdateParameterModeDetail(messageParameterControlAuto, StringSerialNumerInTableProjectSetup,Topic_Control_Setup_Auto_Feedback, host, port, username, password):
    # Global variables
    global gIntValueThresholdZeroExport, gIntValueOffsetZeroExport, gIntValuePowerLimit, gIntValueOffsetPowerLimit, gIntValueTotalPowerInALLInv
    # Local variables
    topicPudUpdateParameterModeDetail = StringSerialNumerInTableProjectSetup + Topic_Control_Setup_Auto_Feedback
    timeStamp = get_utc()
    stringAutoMode = ""
    intComment = 0
    token = ""
    ValueOffsetZeroExportTemp = 0.0
    ValueThresholdZeroExportTemp = 0.0
    ValueOffsetPowerLimitTemp = 0.0
    ValuePowerLimitTemp = 0.0
    
    arrayResultUpdateParameterZeroExportInTableProjectSetUp = []
    arrayResultUpdateParameterPowerLimitInTableProjectSetUp = []
    try:
        if messageParameterControlAuto and 'mode' in messageParameterControlAuto and 'offset' in messageParameterControlAuto:
            stringAutoMode = int(messageParameterControlAuto['mode'])
            token = messageParameterControlAuto['token']
            if stringAutoMode == 1:
                ValueOffsetZeroExportTemp,ValueThresholdZeroExportTemp,arrayResultUpdateParameterZeroExportInTableProjectSetUp = await control_init.handle_zero_export_mode(messageParameterControlAuto)
            elif stringAutoMode == 2:
                ValueOffsetPowerLimitTemp,ValuePowerLimitTemp,arrayResultUpdateParameterPowerLimitInTableProjectSetUp = await control_init.handle_power_limit_mode(messageParameterControlAuto,gIntValueTotalPowerInALLInv)
            # Feedback to MQTT
            if (arrayResultUpdateParameterZeroExportInTableProjectSetUp is None or 
                arrayResultUpdateParameterPowerLimitInTableProjectSetUp is None or 
                (gIntValuePowerLimit is not None and gIntValuePowerLimit > gIntValueTotalPowerInALLInv and stringAutoMode == 2)):
                intComment = 400 
            else:
                intComment = 200
                gIntValueOffsetZeroExport = ValueOffsetZeroExportTemp
                gIntValueThresholdZeroExport = ValueThresholdZeroExportTemp
                gIntValuePowerLimit = ValuePowerLimitTemp
                gIntValueOffsetPowerLimit = ValueOffsetPowerLimitTemp
            # Object Sent MQTT
            objectSend = {
                "time_stamp": timeStamp,
                "status": intComment,
                "token" : token
            }
            # Push MQTT
            mqtt_public_paho_zip(host, port, topicPudUpdateParameterModeDetail, username, password, objectSend)
            push_data_to_mqtt(host, port, topicPudUpdateParameterModeDetail + "Binh", username, password, objectSend)
    except Exception as err:
        print(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'")
# Describe processUpdateModeDetail 
# 	 * @description processUpdateModeDetail
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup, host ,port ,username ,password}
# 	 * @return MySQL_Update enable_zero_export ,enable_power_limit
# 	 */ 
async def processUpdateModeDetail(messageModeControlAuto,StringSerialNumerInTableProjectSetup, host ,port ,username ,password ):
    # Global variables
    global gIntControlModeDetail,Topic_Control_Setup_Mode_Write_Detail_Feedback
    # Local variables
    topicPudModeDetail = StringSerialNumerInTableProjectSetup + Topic_Control_Setup_Mode_Write_Detail_Feedback
    timeStamp = get_utc()
    stringAutoMode = ""
    intComment = 0
    token = ""
    arrayResultUpdateModeDetailInTableProjectSetUp = []
    # Receve data from mqtt
    try:
        if messageModeControlAuto and 'control_mode' in messageModeControlAuto :
            stringAutoMode = messageModeControlAuto['control_mode'] 
            token = messageModeControlAuto["token"]
            stringAutoMode = int(stringAutoMode)
            # Compare get information update database 
            if stringAutoMode == 1:
                gIntControlModeDetail = 1
            elif stringAutoMode == 2:
                gIntControlModeDetail = 2 
            # write mode detail in database
            arrayResultUpdateModeDetailInTableProjectSetUp = MySQL_Update_V1("update project_setup set control_mode = %s", (gIntControlModeDetail,))
            # When you receive one of the above information, give feedback to mqtt
            if arrayResultUpdateModeDetailInTableProjectSetUp == None :
                intComment = 400 
            else:
                intComment = 200 
            objectSend = {
                        "time_stamp" :timeStamp,
                        "status":intComment, 
                        "token":token
                        }
            mqtt_public_paho_zip(host,
                    port,
                    topicPudModeDetail ,
                    username,
                    password,
                    objectSend)
    except Exception as err:
        print(f"Error MQTT subscribe processUpdateModeDetail: '{err}'")
# Describe initializeValueControlAuto 
# 	 * @description initializeValueControlAuto
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return enable_zero_export ,gIntValueOffsetZeroExport,enable_power_limit,gIntValuePowerLimit,gIntValueOffsetPowerLimit
# 	 */ 
async def initializeValueControlAuto():
    # Global variables
    global gIntControlModeDetail,gIntValueOffsetZeroExport,gIntValuePowerLimit,gIntValueOffsetPowerLimit,gIntValueThresholdZeroExport,\
    Kp,Ki,Kd,dt,gIntValueSettingArlamLowPerformance,gIntValueSettingArlamHighPerformance,gStringModeSystempCurrent
    # Local variables
    gIntValuePowerLimit_temp = 0
    arrayResultInitializeParameterZeroExportInTableProjectSetUp = []
    # Get database information the first time
    try:
        arrayResultInitializeParameterZeroExportInTableProjectSetUp = await MySQL_Select_v1("select * from project_setup")
        if arrayResultInitializeParameterZeroExportInTableProjectSetUp:
            gStringModeSystempCurrent = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["mode"]
            gIntControlModeDetail = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["control_mode"]
            gIntValueOffsetZeroExport = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_zero_export"]
            gIntValuePowerLimit_temp = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_power_limit"]
            gIntValueOffsetPowerLimit = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_power_limit"]
            if gIntValueOffsetPowerLimit != None and gIntValuePowerLimit_temp != None :
                gIntValuePowerLimit = (gIntValuePowerLimit_temp - (gIntValuePowerLimit_temp*gIntValueOffsetPowerLimit)/100)
            else:
                gIntValuePowerLimit = 0.0
            gIntValueThresholdZeroExport = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["threshold_zero_export"]
            Kp = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["kp_zero_export"]
            Ki = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["ki_zero_export"]
            Kd = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["kd_zero_export"]
            dt = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["delta_time_zero_export"]
            gIntValueSettingArlamLowPerformance = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["low_performance"]
            gIntValueSettingArlamHighPerformance = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["high_performance"]
    except Exception as err:
        print(f"Error MQTT subscribe initializeValueControlAuto: '{err}'")   
# Describe process_zero_export_power_limit 
# 	 * @description process_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return chosse process zero_export ,power_limit ,zero_export + power_limit , Auto - Full P
# 	 */ 
async def automatedParameterManagement(StringSerialNumerInTableProjectSetup,Topic_Control_WriteAuto,host ,port ,username ,password):
    # Global variables 
    global gIntControlModeDetail
    # Select the auto run process
    if gIntControlModeDetail == 1 :
        print("==============================zero_export==============================")
        await processCaculatorPowerForInvInZeroExportMode(StringSerialNumerInTableProjectSetup,Topic_Control_WriteAuto,host ,port ,username ,password)
    else:
        print("==============================power_limit==============================")
        await processCaculatorPowerForInvInPowerLimitMode(StringSerialNumerInTableProjectSetup,Topic_Control_WriteAuto,host ,port ,username ,password)
############################################################################ Sud MQTT ############################################################################
# Describe processMessage 
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def processMessage(topic, message,StringSerialNumerInTableProjectSetup,topic1,topic2,topic3,topic4,\
    topic5,topic6,topic7,topic8,topic9,topic10,topic11,topic12,topic13,topic14,topic15,topic16,topic17,host,port,username,password):
    global gArrayMessageAllDevice
    topics = [
            StringSerialNumerInTableProjectSetup + topic1,
            StringSerialNumerInTableProjectSetup + topic2,
            StringSerialNumerInTableProjectSetup + topic3,
            StringSerialNumerInTableProjectSetup + topic4,
            StringSerialNumerInTableProjectSetup + topic5,
            StringSerialNumerInTableProjectSetup + topic6,
            StringSerialNumerInTableProjectSetup + topic7,
            StringSerialNumerInTableProjectSetup + topic8,
            StringSerialNumerInTableProjectSetup + topic9,
            StringSerialNumerInTableProjectSetup + topic10
        ]
    try:
        if topic == topics[0]:  # topic1
            await subSystempModeWhenUserChangeModeSystemp(message,StringSerialNumerInTableProjectSetup,topic12, host, port, username, password)
        elif topic == topics[1]:  # topic2
            await pudInformationProjectSetupWhenRequest(message, StringSerialNumerInTableProjectSetup, host, port, username, password)
        elif topic == topics[2]:  # topic3
            await processUpdateParameterModeDetail(message, StringSerialNumerInTableProjectSetup,topic15, host, port, username, password)
        elif topic == topics[3]:  # topic4
            gArrayMessageAllDevice = message
            await getListALLInvInProject(gArrayMessageAllDevice, StringSerialNumerInTableProjectSetup,topic14, host, port, username, password)
            await getValueProductionAndConsumtion(gArrayMessageAllDevice,StringSerialNumerInTableProjectSetup,topic11,host,port,username,password)
            # await getIPCHardwareInformation(StringSerialNumerInTableProjectSetup,topic16, host, port, username, password)
            # await automatedParameterManagement(StringSerialNumerInTableProjectSetup,topic17, host, port, username, password)
        elif topic == topics[4]:  # topic5
            pass
        elif topic == topics[5]:  # topic6
            await insertInformationProjectSetupWhenRequest(message, StringSerialNumerInTableProjectSetup, host, port, username, password)
        elif topic == topics[6]:  # topic7
            await processUpdateModeDetail(message, StringSerialNumerInTableProjectSetup, host, port, username, password)
        elif topic in topics[7:]:  # topic8, topic9, topic10
            await pudSystempModeTrigerEachDeviceChange(message, StringSerialNumerInTableProjectSetup,topic13, host, port, username, password)
    except Exception as err:
        print(f"Error MQTT subscribe processMessage: '{err}'") 
# Describe gzip_decompress 
# 	 * @description gzip_decompress 
# 	 * @author bnguyen 
# 	 * @since 2-05-2024 
# 	 * @param {message} 
# 	 * @return result_list 
# 	 */ 
def gzip_decompress(message):
    try:
        result_decode=base64.b64decode(message.decode('ascii'))
        result_decompress=gzip.decompress(result_decode)
        return json.loads(result_decompress)
    except Exception as err:
        print(f"decompress: '{err}'")
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processHandleMessagesDriver(client,StringSerialNumerInTableProjectSetup,topic1,topic2,topic3,topic4,topic5,\
    topic6,topic7,topic8,topic9,topic10,topic11,topic12,topic13,topic14,topic15,topic16,topic17,host,port,username,password):
    
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = gzip_decompress(message.message)
            await processMessage(topic, payload, StringSerialNumerInTableProjectSetup,topic1,topic2,topic3,topic4,topic5,\
                topic6,topic7,topic8,topic9,topic10,topic11,topic12,topic13,topic14,topic15,topic16,topic17,host,port,username,password)
    except Exception as err:
        print(f"Error processHandleMessagesDriver: '{err}'")
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processSudAllMessageFromMQTT(host, port, username, password, StringSerialNumerInTableProjectSetup,topic1,\
    topic2,topic3,topic4,topic5,topic6,topic7,topic8,topic9,topic10,topic11,topic12,topic13,topic14,topic15,topic16,topic17):
    
    arrayTopic = [StringSerialNumerInTableProjectSetup + topic1, StringSerialNumerInTableProjectSetup + topic2,\
                StringSerialNumerInTableProjectSetup +topic3, StringSerialNumerInTableProjectSetup +topic4, \
                StringSerialNumerInTableProjectSetup +topic5, StringSerialNumerInTableProjectSetup +topic6, \
                StringSerialNumerInTableProjectSetup +topic7, StringSerialNumerInTableProjectSetup +topic8, \
                StringSerialNumerInTableProjectSetup +topic9, StringSerialNumerInTableProjectSetup +topic10]
    try:
        client = mqttools.Client(
            host=host,
            port=port,
            username=username,
            password=bytes(password, 'utf-8'),
            subscriptions=arrayTopic,
            connect_delays=[1, 2, 4, 8]
        )
        while True:
            await client.start()
            await processHandleMessagesDriver(client, StringSerialNumerInTableProjectSetup,topic1,topic2,topic3,topic4,topic5,\
                topic6,topic7,topic8,topic9,topic10,topic11,topic12,topic13,topic14,topic15,topic16,topic17,host, port, username, password)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT processSudAllMessageFromMQTT: '{err}'")

async def main():
    # Initialize values ​​for global variables
    await initializeValueControlAuto()
    # Get Serial number From DB
    db_new=await db_config.get_db()
    project_init=project_service.ProjectService()
    results_project=await project_init.project_inform(db_new)
    # Run Task
    if results_project != None :
        StringSerialNumerInTableProjectSetup=results_project["serial_number"]
        # Cycle
        scheduler = AsyncIOScheduler()
        scheduler.add_job(getIPCHardwareInformation, 'cron',  second = f'*/1' , args=[StringSerialNumerInTableProjectSetup,
                                                                            Topic_CPU_Information,
                                                                            Mqtt_Broker,
                                                                            Mqtt_Port,
                                                                            Mqtt_UserName,
                                                                            Mqtt_Password])
        scheduler.add_job(automatedParameterManagement, 'cron',  second = f'*/5' , args=[StringSerialNumerInTableProjectSetup,
                                                                            Topic_Control_WriteAuto,
                                                                            Mqtt_Broker,
                                                                            Mqtt_Port,
                                                                            Mqtt_UserName,
                                                                            Mqtt_Password])
        scheduler.start()
        tasks = []
        tasks.append(asyncio.create_task(processSudAllMessageFromMQTT(
                                                Mqtt_Broker,
                                                Mqtt_Port,
                                                Mqtt_UserName,
                                                Mqtt_Password,
                                                StringSerialNumerInTableProjectSetup,
                                                Topic_Control_Setup_Mode_Write,
                                                Topic_Project_Get,
                                                Topic_Control_Setup_Auto,
                                                Topic_Devices_All,
                                                Topic_CPU_Get,
                                                Topic_Project_Set,
                                                Topic_Control_Setup_Mode_Write_Detail,
                                                Topic_Control_Feedback ,
                                                Topic_Control_Modify,
                                                Topic_Control_FeedbackSetup,
                                                Topic_Meter_Monitor,
                                                Topic_Control_Setup_Mode_Feedback,
                                                Topic_Control_Setup_Mode_Write,
                                                Topic_Control_Process,
                                                Topic_Control_Setup_Auto_Feedback,
                                                Topic_CPU_Information,
                                                Topic_Control_WriteAuto
                                                )))
        await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())