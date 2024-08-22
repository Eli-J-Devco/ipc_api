# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import collections
import datetime
import os
import sys
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from configs.config import MQTTSettings, MQTTTopicSUD,MQTTTopicPUSH
from utils.MQTTService import *
from utils.libMySQL import *
from utils.libTime import *
from cpu.cpu_service import *
from control.control_service import *

arr = sys.argv # Variables Array System
gStringModeSystempCurrent = ""
gFloatValueSystemPerformance = 0
serialNumber = ""
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
mqtt_service = None 
# Infor Configuration
Mqtt_Broker = Config.MQTT_BROKER
Mqtt_Port = Config.MQTT_PORT
Mqtt_Topic = Config.MQTT_TOPIC +"/Dev/"
Mqtt_UserName = Config.MQTT_USERNAME
Mqtt_Password = Config.MQTT_PASSWORD

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
async def getIPCHardwareInformation(mqtt_service,Topic_CPU_Information):
    global net_io_counters_prev, disk_io_counters_prev 
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
        system_info["SystemInformation"] = CPUInfo.getSystemInformation()
        system_info["BootTime"] = CPUInfo.getBootTime() or {}
        system_info["CPUInfo"] = CPUInfo.getCpuInformation() or {}
        system_info["MemoryInformation"] = CPUInfo.getMemoryInformation() or {}
        system_info["DiskInformation"] = CPUInfo.getDiskInformation() or {}
        system_info["NetworkInformation"] = CPUInfo.getNetworkInformation() or {}
        system_info["NetworkSpeed"] = CPUInfo.getNetworkSpeedInformation(net_io_counters_prev) or {}
        system_info["DiskIO"] = CPUInfo.getDiskIoInformation(disk_io_counters_prev) or {}
        # Check that all fields are not None
        # if all(system_info.values()):
            # Push system_info to MQTT 
        MQTTService.push_data(mqtt_service,Topic_CPU_Information + "Binh",system_info)
        MQTTService.push_data_zip(mqtt_service,Topic_CPU_Information,system_info)
    except Exception as err:
        print(f"Error MQTT subscribe getCpuInformation: '{err}'")
############################################################################ Mode Systemp ############################################################################
# Describe pudSystempModeTrigerEachDeviceChange
# /**
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 02-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup,host, port, username, password}
# 	 * @return push message systemp when user changes mode each device
# 	 */
async def pudSystempModeTrigerEachDeviceChange(mqtt_service,MessageCheckModeSystemp,Topic_Control_Setup_Mode_Write):
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
            MQTTService.push_data_zip(mqtt_service,Topic_Control_Setup_Mode_Write,data_send)
        except asyncio.TimeoutError:
            print("Timeout waiting for data from MySQL")
############################################################################ Config SiteInfo ############################################################################
# Describe insertInformationProjectSetup 
# 	 * @description insertInformationProjectSetup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result, host, port, topicPublic, username, password}
# 	 * @return data_send
# 	 */ 
async def insertInformationProjectSetup(mqtt_service,messageInsertInformationProjectSetup,Topic_Project_Set_Feedback):
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
                    current_time = get_utc()
                    data_send = {
                        "status": 400,
                        "time_stamp": current_time
                    }
                else:
                    current_time = get_utc()
                    data_send = {
                        "status": 200,
                        "time_stamp": current_time
                    }
        MQTTService.push_data_zip(mqtt_service,Topic_Project_Set_Feedback,data_send)
    except Exception as err:
        print(f"Error MQTT subscribe insertInformationProjectSetup: '{err}'")
# Describe insertInformationProjectSetupWhenRequest 
# 	 * @description insertInformationProjectSetupWhenRequest
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result ,StringSerialNumerInTableProjectSetup,host, port, username, password}
# 	 * @return call insertInformationProjectSetup
# 	 */ 
async def insertInformationProjectSetupWhenRequest(mqtt_service , messageInsertInformationProjectSetup, Topic_Project_Set_Feedback):
    try:
        if messageInsertInformationProjectSetup and 'set_information' in messageInsertInformationProjectSetup:
            await insertInformationProjectSetup(mqtt_service,messageInsertInformationProjectSetup,Topic_Project_Set_Feedback)    
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
            listAutoDevice = GetListAutoDevice()
            device_info = listAutoDevice.extract_device_auto_info(item)
            if not device_info:
                continue
            # Get Information Each Device 
            id_device, mode, status_device, p_max_custom, p_min, value, operator, slope, results_device_type = device_info
            # Check Device Auto 
            if listAutoDevice.is_device_controlable(results_device_type, status_device, mode, operator):
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
async def getListALLInvInProject( mqtt_service ,messageAllDevice,Topic_Control_Process):
    global gIntValueProductionSystemp, gIntValueSettingArlamLowPerformance,gIntValueSettingArlamHighPerformance,\
        gIntValueTotalPowerInALLInv,gStringModeSystempCurrent,gIntValueTotalPowerInInvInManMode,gIntValueTotalPowerInInvInAutoMode,gFloatValueSystemPerformance
    ArrayDeviceList = []
    # Get Informatio about the device
    if messageAllDevice and isinstance(messageAllDevice, list):
        for item in messageAllDevice:
            ListAllDevice = GetListAllDevice()
            device_info = ListAllDevice.extract_device_all_info(item)
            if device_info:
                ArrayDeviceList.append(device_info)
    # Calculate the sum of wmax values ​​of all inv in the system
    gIntValueTotalPowerInALLInv,gIntValueTotalPowerInInvInManMode = ListAllDevice.calculate_total_wmax(ArrayDeviceList,gIntValueTotalPowerInInvInAutoMode)
    # Call the update_system_performance function and get the return value
    gFloatValueSystemPerformance, StringMessageStatusSystemPerformance, intStatusSystemPerformance = ListAllDevice.update_system_performance(
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
    MQTTService.push_data_zip(mqtt_service,Topic_Control_Process,result)
    return ArrayDeviceList
# Describe getValueProductionAndConsumtion 
# 	 * @description getValueProductionAndConsumtion
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return value_production ,value_consumption
# 	 */ 
############################################################################ Get Value Metter ############################################################################
async def getValueProductionAndConsumtion(mqtt_service , gArrayMessageAllDevice, Topic_Meter_Monitor):
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
                result_type_meter = ValueEnergySystem.get_device_type(id_device)
                if result_type_meter:
                    IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production = ValueEnergySystem.calculate_production(item, result_type_meter, IntTotalValueProduction, IntIntegralValueProduction, last_update_time_production, current_time)
                    IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption = ValueEnergySystem.calculate_consumption(item, result_type_meter, IntTotalValueConsumtion, IntIntegralValueConsumtion, last_update_time_comsumption, current_time)
        # Update the global values ​​of total production and total consumption
        gIntValueProductionSystemp = IntTotalValueProduction
        gIntValueConsumptionSystemp = IntTotalValueConsumtion
    try:
        ValueProductionAndConsumtion = ValueEnergySystem.message_value_metter(gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp)
        # Push system_info to MQTT
        MQTTService.push_data_zip(mqtt_service,Topic_Meter_Monitor,ValueProductionAndConsumtion)
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
async def processCaculatorPowerForInvInPowerLimitMode(mqtt_service,Topic_Control_WriteAuto):
    global gArrayMessageAllDevice, gIntValuePowerLimit, gIntValueProductionSystemp, gIntValueTotalPowerInInvInAutoMode,\
    gStringModeSystempCurrent, gFloatValueSystemPerformance,gIntValueTotalPowerInInvInManMode,gIntControlModeDetail
    # Local variables
    gArraydevices = []
    gIntValuePowerForEachInvInModePowerLimit = 0 
    # Get List Device Can Control 
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
    # Caculator System Performance 
    if gStringModeSystempCurrent != 0:
        gFloatValueSystemPerformance = await FuntionCaculatorPower.calculate_system_performance(gStringModeSystempCurrent,gFloatValueSystemPerformance,\
        gIntValueProductionSystemp,gIntValuePowerLimit)
    # Get Infor Device Control 
    if gArraydevices:
        listInvControlPowerLimitMode = []
        for device in gArraydevices:
            id_device, mode, intPowerMaxOfInv = FuntionCaculatorPower.process_device_powerlimit_info(device)
            gIntValuePowerForEachInvInModePowerLimit = FuntionCaculatorPower.calculate_power_value(intPowerMaxOfInv,gStringModeSystempCurrent,gIntValueTotalPowerInInvInManMode,\
                gIntValueTotalPowerInInvInAutoMode,gIntValuePowerLimit)
            # Create Infor Device Publish MQTT
            if gIntValueProductionSystemp < gIntValuePowerLimit:
                item = FuntionCaculatorPower.create_control_item(gIntControlModeDetail,device, gIntValuePowerForEachInvInModePowerLimit,gIntValuePowerLimit,\
                    gIntValueTotalPowerInInvInManMode,gIntValueProductionSystemp)
            else:
                item = {
                    "id_device": id_device,
                    "mode": mode,
                    "status": "power limit",
                    "setpoint": gIntValuePowerLimit - gIntValueTotalPowerInInvInManMode,
                    "feedback": gIntValueProductionSystemp,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": max(0, gIntValuePowerForEachInvInModePowerLimit - (gIntValueProductionSystemp - gIntValuePowerLimit))}
                    ]
                }
            # Create List Device 
            listInvControlPowerLimitMode.append(item)
        # Push MQTT
        if len(gArraydevices) == len(listInvControlPowerLimitMode):
            MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlPowerLimitMode)
            MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto,listInvControlPowerLimitMode)
############################################################################ Zero Export Control ############################################################################
# Describe processCaculatorPowerForInvInZeroExportMode 
# 	 * @description processCaculatorPowerForInvInZeroExportMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return gIntValuePowerForEachInvInModeZeroExport
# 	 */ 
async def processCaculatorPowerForInvInZeroExportMode(mqtt_service,Topic_Control_WriteAuto):
    global gArrayMessageAllDevice, gIntValueThresholdZeroExport, gIntValueOffsetZeroExport, gIntValueConsumptionSystemp,\
        gIntValueProductionSystemp, gIntValueTotalPowerInInvInAutoMode,gListMovingAverageConsumption, gIntValueTotalPowerInInvInManMode, \
        gStringModeSystempCurrent, gFloatValueSystemPerformance
    # Local variables
    gArraydevices = []
    gIntValuePowerForEachInvInModeZeroExport = 0
    intPracticalConsumptionValue = 0.0
    setpointCalculatorPowerForEachInv = 0 
    # Get Setpoint ,Value Consumption System 
    if gIntValueConsumptionSystemp:
        setpointCalculatorPowerForEachInv, intPracticalConsumptionValue = await FuntionCaculatorPower.calculate_setpoint(gStringModeSystempCurrent,gIntValueConsumptionSystemp,gIntValueTotalPowerInInvInManMode,\
        gListMovingAverageConsumption,gMaxValueChangeSetpoint,gIntValueOffsetZeroExport)
    # Get List Device Can Control 
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
    # Caculator System Performance 
    if gStringModeSystempCurrent != 0:
        gFloatValueSystemPerformance = await FuntionCaculatorPower.calculate_system_performance(gStringModeSystempCurrent,gFloatValueSystemPerformance,\
        gIntValueProductionSystemp,intPracticalConsumptionValue)
    if gArraydevices:
        listInvControlZeroExportMode = []
        for device in gArraydevices:
            id_device, mode, intPowerMaxOfInv = FuntionCaculatorPower.process_device_powerlimit_info(device)
            gIntValuePowerForEachInvInModeZeroExport = FuntionCaculatorPower.calculate_power_value(intPowerMaxOfInv, gStringModeSystempCurrent, 
                gIntValueTotalPowerInInvInManMode, gIntValueTotalPowerInInvInAutoMode, setpointCalculatorPowerForEachInv)
            # Create Infor Device Publish MQTT
            if gIntValueProductionSystemp < intPracticalConsumptionValue and \
                gIntValueConsumptionSystemp >= gIntValueThresholdZeroExport and gIntValueConsumptionSystemp >= 0:
                item = FuntionCaculatorPower.create_control_item(gIntControlModeDetail,device, gIntValuePowerForEachInvInModeZeroExport,setpointCalculatorPowerForEachInv,\
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
            MQTTService.push_data_zip(mqtt_service,Topic_Control_WriteAuto,listInvControlZeroExportMode)
            MQTTService.push_data(mqtt_service,Topic_Control_WriteAuto,listInvControlZeroExportMode)
############################################################################ Setup Parameter Control ############################################################################
# Describe processUpdateParameterModeDetail 
# 	 * @description processUpdateParameterModeDetail
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup, host ,port ,username ,password}
# 	 * @return MySQL_Update gIntValueOffsetZeroExport,gIntValuePowerLimit,gIntValueOffsetPowerLimit
# 	 */ 
async def processUpdateParameterModeDetail(mqtt_service,messageParameterControlAuto,Topic_Control_Setup_Auto_Feedback):
    # Global variables
    global gIntValueThresholdZeroExport, gIntValueOffsetZeroExport, gIntValuePowerLimit, gIntValueOffsetPowerLimit, gIntValueTotalPowerInALLInv
    # Local variables
    timeStamp = get_utc()
    stringAutoMode = ""
    intComment = 0
    arrayResultUpdateParameterZeroExportInTableProjectSetUp = []
    arrayResultUpdateParameterPowerLimitInTableProjectSetUp = []
    try:
        if messageParameterControlAuto and 'mode' in messageParameterControlAuto and 'offset' in messageParameterControlAuto:
            stringAutoMode = int(messageParameterControlAuto['mode'])
            if stringAutoMode == 1:
                gIntValueOffsetZeroExport,gIntValueThresholdZeroExport,arrayResultUpdateParameterZeroExportInTableProjectSetUp = await ModeDetailHandler.handle_zero_export_mode(messageParameterControlAuto)
            elif stringAutoMode == 2:
                gIntValueOffsetPowerLimit,gIntValuePowerLimit,arrayResultUpdateParameterPowerLimitInTableProjectSetUp = await ModeDetailHandler.handle_power_limit_mode(messageParameterControlAuto,gIntValueTotalPowerInALLInv)
            # Feedback to MQTT
            if arrayResultUpdateParameterZeroExportInTableProjectSetUp == None or arrayResultUpdateParameterPowerLimitInTableProjectSetUp == None or (gIntValuePowerLimit != None and gIntValuePowerLimit > gIntValueTotalPowerInALLInv and stringAutoMode == 2):
                intComment = 400 
            else:
                intComment = 200 
            # Object Sent MQTT
            objectSend = {
                "time_stamp": timeStamp,
                "status": intComment,
            }
            # Push MQTT
            MQTTService.push_data_zip(mqtt_service,Topic_Control_Setup_Auto_Feedback,objectSend)
    except Exception as err:
        print(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'") 
# Describe process_zero_export_power_limit 
# 	 * @description process_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return chosse process zero_export ,power_limit ,zero_export + power_limit , Auto - Full P
# 	 */ 
async def automatedParameterManagement(mqtt_service,Topic_Control_WriteAuto):
    # Global variables 
    global gIntControlModeDetail
    # Select the auto run process
    if gIntControlModeDetail == 1 :
        print("==============================zero_export==============================")
        await processCaculatorPowerForInvInZeroExportMode(mqtt_service,Topic_Control_WriteAuto)
    else:
        print("==============================power_limit==============================")
        await processCaculatorPowerForInvInPowerLimitMode(mqtt_service,Topic_Control_WriteAuto)
############################################################################ Sud MQTT ############################################################################
# Describe processMessage 
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def processMessage(mqtt_service,serial_number ,topic, message):
    global gArrayMessageAllDevice
    global gStringModeSystempCurrent
    global gIntControlModeDetail
    topicSudMQTT = MQTTTopicSUD()
    topicPushMQTT = MQTTTopicPUSH()
    try:
        if topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE:  # ok 
            gStringModeSystempCurrent = await ModeSystem.processModeSystemChange(mqtt_service,message, topicPushMQTT.MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODEGET_INFORMATION:   # topic2
            await ProjectSetupService.pudFeedBackProjectSetup(mqtt_service,topicPushMQTT.MQTT_TOPIC_PUD_PROJECT_SETUP)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO:   # topic3
            await processUpdateParameterModeDetail(mqtt_service,message)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_DEVICES_ALL:   # topic4
            gArrayMessageAllDevice = message
            # print("message",message)
            await getListALLInvInProject(mqtt_service,gArrayMessageAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS)
            await getValueProductionAndConsumtion(mqtt_service,gArrayMessageAllDevice,topicPushMQTT.MQTT_TOPIC_PUD_MONIT_METER)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE:   # topic6
            await insertInformationProjectSetupWhenRequest(mqtt_service,message)
        elif topic == serial_number + topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL:   # topic7
            gIntControlModeDetail = await ModeDetailHandler.processUpdateModeControlDetail(mqtt_service,message)
        elif topic in serial_number + topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE:   # topic8, topic9, topic10
            await ModeSystem.pudSystempModeTrigerEachDeviceChange(mqtt_service ,topicPushMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE)
    except Exception as err:
        print(f"Error MQTT subscribe processMessage: '{err}'") 
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processSudAllMessageFromMQTT(mqtt_service,serialnumber):
    while True:
        try:
            # Gọi hàm sud_data để bắt đầu nhận dữ liệu
            while True:
                topic, message = await MQTTService.sud_data(mqtt_service)
                if message and topic:
                    await processMessage(mqtt_service, serialnumber, topic, message)
        except Exception as err:
            print(f"Error in MQTT service: '{err}'")
            print("Trying to reconnect in 5 seconds...")
            await asyncio.sleep(5)
async def main():
    global gStringModeSystempCurrent
    global gIntControlModeDetail
    global gIntValueOffsetZeroExport
    global gIntValuePowerLimit_temp
    global gIntValueOffsetPowerLimit
    global gIntValuePowerLimit
    global gIntValueThresholdZeroExport
    global gIntValueSettingArlamLowPerformance
    global gIntValueSettingArlamHighPerformance
    
    # Initialize values ​​for global variables
    initialized_values = await ProjectSetupService.initializeValueControlAuto()
    if initialized_values:
        serialNumber = initialized_values["serial_number"]
        gStringModeSystempCurrent = initialized_values["mode"]
        gIntControlModeDetail = initialized_values["control_mode"]
        gIntValueOffsetZeroExport = initialized_values["value_offset_zero_export"]
        gIntValuePowerLimit_temp = initialized_values["value_power_limit"]
        gIntValueOffsetPowerLimit = initialized_values["value_offset_power_limit"]
        gIntValuePowerLimit = (gIntValuePowerLimit_temp - (gIntValuePowerLimit_temp * gIntValueOffsetPowerLimit) / 100)
        gIntValueThresholdZeroExport = initialized_values["threshold_zero_export"]
        gIntValueSettingArlamLowPerformance = initialized_values["low_performance"]
        gIntValueSettingArlamHighPerformance = initialized_values["high_performance"]
    else:
        print("Failed to initialize values.")
    # Run Task
    if serialNumber != None :
        parameterMQTT = MQTTSettings()
        topicSudMQTT = MQTTTopicSUD()
        topicPushMQTT = MQTTTopicPUSH()
        # Khởi tạo dịch vụ MQTT
        mqtt_service = MQTTService(
            host=parameterMQTT.MQTT_BROKER,
            port=parameterMQTT.MQTT_PORT,
            username=parameterMQTT.MQTT_USERNAME,
            password=parameterMQTT.MQTT_PASSWORD,
            serial_number=serialNumber  # Thay thế bằng serial number thực tế
        )
        # Đặt các topic SUD
        mqtt_service.set_topics(
            topicSudMQTT.MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
            topicSudMQTT.MQTT_TOPIC_SUD_MODEGET_INFORMATION,
            topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL,
            topicSudMQTT.MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
            topicSudMQTT.MQTT_TOPIC_SUD_DEVICES_ALL,
            topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN,
            topicSudMQTT.MQTT_TOPIC_SUD_FEEDBACK_CONTROL_MAN_SETUP,
            topicSudMQTT.MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE,
            topicSudMQTT.MQTT_TOPIC_SUD_SETTING_ARLAM,
            topicSudMQTT.MQTT_TOPIC_SUD_MODIFY_DEVICE
        )
        # Cycle
        scheduler = AsyncIOScheduler()
        # scheduler.add_job(getIPCHardwareInformation, 'cron',  second = f'*/1' , args=[mqtt_service,
        #                                                                     topicPushMQTT.MQTT_TOPIC_PUD_CPU_SETUP,])
        scheduler.add_job(automatedParameterManagement, 'cron',  second = f'*/5' , args=[mqtt_service,
                                                                            topicPushMQTT.MQTT_TOPIC_PUD_CONTROL_AUTO,])
        scheduler.start()
        tasks = []
        tasks.append(asyncio.create_task(processSudAllMessageFromMQTT(
                                        mqtt_service,
                                        serialNumber
                                        )))
        await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())