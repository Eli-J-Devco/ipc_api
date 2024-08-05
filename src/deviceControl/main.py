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

arr = sys.argv # Variables Array System
gStringModeSysTemp = ""
gStringModeSystempCurrent = ""
gArraygArraydevices = []
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
gIntValueProduction1Minute = 0
gIntValueConsumption1Minute = 0
gIntValueProduction1Hour = 0
gIntValueConsumption1Hour = 0
gIntValueProductionDaily = 0
gIntValueConsumptionDaily = 0 
gIntValueProductionInModeZeroExport = 0
gIntValueConsumtionInModeZeroExport = 0
gIntValueProductionInModePowerLimit = 0
gIntValueConsumtionInModePowerLimit = 0
gFloatValueMaxPredictProductionInstant = 0.0
start_time_minutely = time.time()
start_time_hourly = time.time()
start_time_daily = time.time()
cycle_time1s = time.time()

# Parameters Value Power In Inv Each Mode 
gIntValueTotalPowerInInvInAutoMode = 0
gIntValueTotalPowerInALLInv = 0
gIntValuePowerForEachInvInModeZeroExport = 0
gIntValuePowerForEachInvInModePowerLimit = 0
gIntValueTotalPowerInInvInManMode = 0
gArrayMessageChangeModeSystemp = []
gArrayMessageAllDevice = []
gArrayResultExecuteSQLModeSysTemp = []
gArrayResultExecuteSQLModeDevice = []
gBitManWrite = 0
# Stores information about bytes_sent and bytes_recv of the previous query
net_io_counters_prev = {}
net_io_counters_prev["TotalSent"] = 0
net_io_counters_prev["TotalReceived"] = 0
net_io_counters_prev["Timestamp"] = datetime.datetime.now()

# Stores information about read_count and write_count of the previous query
disk_io_counters_prev = {}
disk_io_counters_prev["ReadCount"] = 0
disk_io_counters_prev["WriteCount"] = 0
disk_io_counters_prev["Timestamp"] = datetime.datetime.now()

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC|device_id|device_name
# Subscribe -> IPC|device_id|device_name|control
MQTT_TOPIC = Config.MQTT_TOPIC +"/Dev/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
MQTT_TOPIC_SUD_MODECONTROL_DEVICE = "/Control/Setup/Mode/Write"
MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL = "/Control/Setup/Mode/Feedback"
MQTT_TOPIC_PUD_PROJECT_SETUP = "/Project/Information"
MQTT_TOPIC_PUD_CPU_SETUP = "/CPU/Information"
MQTT_TOPIC_SUD_MODEGET_INFORMATION = "/Project/Get"
MQTT_TOPIC_SUD_MODEGET_CPU = "/CPU/Get"
MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL = "/Control/Setup/Mode/Write/Detail"
MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK = "/Control/Setup/Mode/Write/Detail/Feedback"
MQTT_TOPIC_SUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto"
MQTT_TOPIC_PUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto/Feedback"
MQTT_TOPIC_SUD_DEVICES_ALL = "/Devices/All"
MQTT_TOPIC_SUD_CONTROL_MAN = "/Control/Write"
MQTT_TOPIC_PUD_CONTROL_AUTO = "/Control/WriteAuto"
MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE = "/Project/Set"
MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE = "/Project/Set/Feedback"
MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS = "/Control/Process"
MQTT_TOPIC_PUD_MONIT_METER = "/Meter/Monitor"
MQTT_TOPIC_SUD_SETTING_ARLAM = "/Control/Alarm/Setting"
MQTT_TOPIC_PUD_SETTING_ARLAM_FEEDBACK = "/Control/Alarm/Feedback"
MQTT_TOPIC_SUD_FEEDBACK_WRITE = "/Control/Write"
MQTT_TOPIC_SUD_MODIFY_DEVICE = "/Control/Modify"

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
# Describe get_size cpu 
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def getReadableSize(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} YB"
# Describe convertBytesToReadable  
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def convertBytesToReadable(bytes_value, unit="KB"):
    if unit == "KB":
        return f"{bytes_value / 1024:.2f} KB"
    elif unit == "MB":
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    elif unit == "GB":
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_value} B"
# Describe getCpuInformation 
# 	 * @description get cpu information
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
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
async def getCpuInformation(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global MQTT_TOPIC_PUD_CPU_SETUP
    topicPublicInformationCpu = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CPU_SETUP
    timeStampPudCpuInformation = get_utc()
    try:
        # Format system_info
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
        # System Information
        uname = platform.uname()
        system_info["SystemInformation"]["System"] = uname.system
        system_info["SystemInformation"]["NodeName"] = uname.node
        system_info["SystemInformation"]["Release"] = uname.release
        system_info["SystemInformation"]["Version"] = uname.version
        system_info["SystemInformation"]["Machine"] = uname.machine
        system_info["SystemInformation"]["Processor"] = uname.processor

        boot_time_timestamp = psutil.boot_time()
        bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
        system_info["BootTime"]["BootTime"] = f"{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}"
        # CPU Information
        system_info["CPUInfo"]["Physicalcores"] = psutil.cpu_count(logical=False)
        system_info["CPUInfo"]["Totalcores"] = psutil.cpu_count(logical=True)
        cpufreq = psutil.cpu_freq()
        system_info["CPUInfo"]["MaxFrequency"] = f"{cpufreq.max:.2f}Mhz"
        system_info["CPUInfo"]["MinFrequency"] = f"{cpufreq.min:.2f}Mhz"
        system_info["CPUInfo"]["CurrentFrequency"] = f"{cpufreq.current:.2f}Mhz"
        system_info["CPUInfo"]["TotalCPUUsage"] = f"{psutil.cpu_percent()}%"
        # Memory Information
        svmem = psutil.virtual_memory()
        system_info["MemoryInformation"]["Total"] = getReadableSize(svmem.total)
        system_info["MemoryInformation"]["Available"] = getReadableSize(svmem.available)
        system_info["MemoryInformation"]["Used"] = getReadableSize(svmem.total - svmem.available)
        system_info["MemoryInformation"]["UsedReal"] = getReadableSize(svmem.used)
        system_info["MemoryInformation"]["Free"] = getReadableSize(svmem.free)
        system_info["MemoryInformation"]["Percentage"] = f"{svmem.percent:.1f}%"

        swap = psutil.swap_memory()
        system_info["MemoryInformation"]["SWAP"] = {
            "Total": getReadableSize(swap.total),
            "Free": getReadableSize(swap.free),
            "Used": getReadableSize(swap.used),
            "Percentage": f"{swap.percent}%"
        }
        # Disk Information
        total_disk_size = 0
        total_disk_used = 0
        disk_partitions = psutil.disk_partitions()
        unique_partitions = {}

        for partition in disk_partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

                partition_key = f"{partition_usage.total}_{partition_usage.used}_{partition_usage.free}"

                if partition_key in unique_partitions:
                    continue

                unique_partitions[partition_key] = {
                    "MountPoint": partition.mountpoint,
                    "TotalSize": getReadableSize(partition_usage.total),
                    "Used": getReadableSize(partition_usage.used),
                    "Free": getReadableSize(partition_usage.free),
                    "Percentage": f"{(partition_usage.used / partition_usage.total) * 100:.1f}%"
                }

                total_disk_size += partition_usage.total
                total_disk_used += partition_usage.used
            except PermissionError:
                continue

        total_disk_info = {
            "TotalSize": getReadableSize(total_disk_size),
            "Used": getReadableSize(total_disk_used),
            "Free": getReadableSize(total_disk_size - total_disk_used),
            "Percentage": f"{(total_disk_used / total_disk_size) * 100:.1f}%"
        }

        system_info["DiskInformation"] = total_disk_info
        # Network Information
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            for address in interface_addresses:
                if str(address.family) == 'AddressFamily.AF_INET':
                    system_info["NetworkInformation"][interface_name] = {
                        "IPAddress": address.address,
                        "Netmask": address.netmask,
                        "BroadcastIP": address.broadcast
                    }
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    system_info["NetworkInformation"][interface_name] = {
                        "MACAddress": address.address,
                        "Netmask": address.netmask,
                        "BroadcastMAC": address.broadcast
                    }
        # Network Speed Information
        net_io_counters = psutil.net_io_counters()
        current_time = datetime.datetime.now()
        time_diff = (current_time - net_io_counters_prev["Timestamp"]).total_seconds()

        system_info["NetworkSpeed"]["Upstream"] = convertBytesToReadable((net_io_counters.bytes_sent - net_io_counters_prev["TotalSent"]) / time_diff , unit="KB")
        system_info["NetworkSpeed"]["Downstream"] = convertBytesToReadable((net_io_counters.bytes_recv - net_io_counters_prev["TotalReceived"]) / time_diff , unit="KB")
        system_info["NetworkSpeed"]["TotalSent"] = getReadableSize(net_io_counters.bytes_sent)
        system_info["NetworkSpeed"]["TotalReceived"] = getReadableSize(net_io_counters.bytes_recv)
        system_info["NetworkSpeed"]["Timestamp"] = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
        
        net_io_counters_prev["TotalSent"] = net_io_counters.bytes_sent
        net_io_counters_prev["TotalReceived"] = net_io_counters.bytes_recv
        net_io_counters_prev["Timestamp"] = current_time
        #  Disk I/O Information
        disk_io_counters = psutil.disk_io_counters()
        current_time = datetime.datetime.now()
        time_diff = (current_time - disk_io_counters_prev["Timestamp"]).total_seconds()

        system_info["DiskIO"]["SpeedRead"] = convertBytesToReadable((disk_io_counters.read_count - disk_io_counters_prev["ReadCount"]) / time_diff , unit="KB")
        system_info["DiskIO"]["SpeedWrite"] = convertBytesToReadable((disk_io_counters.write_count - disk_io_counters_prev["WriteCount"]) / time_diff , unit="KB")
        system_info["DiskIO"]["ReadBytes"] = getReadableSize(disk_io_counters.read_bytes)
        system_info["DiskIO"]["WriteBytes"] = getReadableSize(disk_io_counters.write_bytes)
        system_info["DiskIO"]["Timestamp"] = f"{current_time.hour}:{current_time.minute}:{current_time.second}"

        disk_io_counters_prev["ReadCount"] = disk_io_counters.read_count
        disk_io_counters_prev["WriteCount"] = disk_io_counters.write_count
        disk_io_counters_prev["Timestamp"] = current_time
        # Push system_info to MQTT 
        mqtt_public_paho_zip(mqtt_host,
                            mqtt_port,
                            topicPublicInformationCpu,
                            mqtt_username,
                            mqtt_password,
                            system_info)
        push_data_to_mqtt(mqtt_host,
                            mqtt_port,
                            topicPublicInformationCpu + "Binh",
                            mqtt_username,
                            mqtt_password,
                            system_info)
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
async def subSystempModeWhenUserChangeModeSystemp(StringSerialNumerInTableProjectSetup, host, port, username, password):
    # Global variables
    global gArrayMessageChangeModeSystemp, gStringModeSysTemp, MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL, gArrayResultExecuteSQLModeSysTemp,\
    gArrayResultExecuteSQLModeDevice
    # Local variables
    topicFeedbackModeSystemp = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL
    try:
        if gArrayMessageChangeModeSystemp :
            try:
                if gArrayMessageChangeModeSystemp.get('id_device') == 'Systemp':
                    gStringModeSysTemp = gArrayMessageChangeModeSystemp.get('mode')  
                    querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
                    querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';;"
                    if gStringModeSysTemp in [0, 1, 2]:
                        gArrayResultExecuteSQLModeSysTemp = MySQL_Insert_v5(querysystemp, (gStringModeSysTemp,))
                    else :
                        print("Failed to insert data")
                    if gStringModeSysTemp in [0, 1]:
                        gArrayResultExecuteSQLModeDevice = MySQL_Insert_v5(querydevice, (gStringModeSysTemp,))
                    if gArrayResultExecuteSQLModeSysTemp is None or gArrayResultExecuteSQLModeDevice is None:
                        current_time = get_utc()
                        objectSend = {
                                "status" : 400,
                                "time_stamp" :current_time,
                                }
                        mqtt_public_paho_zip(host,
                                port,
                                topicFeedbackModeSystemp,
                                username,
                                password,
                                objectSend)
            except Exception as json_err:
                print(f"Error processing JSON data: {json_err}")
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
async def pudSystempModeTrigerEachDeviceChange(MessageCheckModeSystemp, StringSerialNumerInTableProjectSetup, host, port, username, password):
    # Global variables
    global MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    # Local variables
    topicpud = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    # Switch to user mode that is both man and auto
    if MessageCheckModeSystemp:
        try:
            # Wait for up to 5 seconds for the data to be available
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
# Describe confirmSystemModeAfterDeviceChangeOrUserChangeModeSystemp 
# 	 * @description confirmSystemModeAfterDeviceChangeOrUserChangeModeSystemp
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return ModeSysTemp
# 	 */ 
async def confirmSystemModeAfterDeviceChangeOrUserChangeModeSystemp(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, \
    topicPublic, mqtt_username, mqtt_password):
    global gStringModeSysTemp, gArrayResultExecuteSQLModeSysTemp, gArrayResultExecuteSQLModeDevice,gStringModeSystempCurrent
    ModeSystempInDB = []
    topicConfirmModeSystemp = StringSerialNumerInTableProjectSetup + topicPublic
    # Get ModeSysTemp from database when start program
    if gArrayResultExecuteSQLModeSysTemp is not None and gArrayResultExecuteSQLModeDevice is not None:
        if not gStringModeSysTemp:
            ModeSystempInDB = await MySQL_Select_v1("SELECT `project_setup`.`mode` FROM `project_setup`")
            gStringModeSysTemp = ModeSystempInDB[0]['mode']
        # Have ModeSysTemp push to mqtt 
        if gStringModeSysTemp in (0, 1, 2):
            gStringModeSystempCurrent = gStringModeSysTemp
            try:
                current_time = get_utc()
                data_send = {
                    "status": 200,
                    "confirm_mode": gStringModeSysTemp,
                    "time_stamp": current_time,
                }
                mqtt_public_paho_zip(mqtt_host, mqtt_port, topicConfirmModeSystemp, mqtt_username, mqtt_password, data_send)
                gStringModeSysTemp = None
            except Exception as err:
                print(f"Error MQTT subscribe confirmSystemModeAfterDeviceChangeOrUserChangeModeSystemp: '{err}'")
############################################################################ Config SiteInfo ############################################################################
# Describe pudFeedBackProjectSetup 
# 	 * @description pudFeedBackProjectSetup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return data_send
# 	 */ 
async def pudFeedBackProjectSetup(mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
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
            mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password, dataSendTopicProjectInformation )
        except Exception as err:
            print(f"Error MQTT subscribe pudFeedBackProjectSetup: '{err}'")
# Describe insertInformationProjectSetup 
# 	 * @description insertInformationProjectSetup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return data_send
# 	 */ 
async def insertInformationProjectSetup(messageInsertInformationProjectSetup, mqtt_host, mqtt_port, topicPublicInformationProjectSetup, mqtt_username, mqtt_password):
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
                mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublicInformationProjectSetup, mqtt_username, mqtt_password, data_send)
        else:
            current_time = get_utc()
            data_send = {
                "status": 200,
                "time_stamp": current_time
            }
            mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublicInformationProjectSetup, mqtt_username, mqtt_password, data_send)
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
    global MQTT_TOPIC_PUD_PROJECT_SETUP
    topicPudAllInformationTableProjectSetup = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_PROJECT_SETUP
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
    global MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE
    topicPudInsertInformationProjectSetupWhenRequest = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE
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
    # Global variables
    global gIntValueTotalPowerInInvInAutoMode
    # Local variables
    ArayyDeviceList = []
    p_min = 0
    # Get results mqtt
    if messageAllDevice and isinstance(messageAllDevice, list):
        for item in messageAllDevice:
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                status_device = item['status_device']
                p_max = item['rated_power']
                if item['rated_power_custom'] != None :
                    p_max_custom = item['rated_power_custom']
                else:
                    p_max_custom = item['rated_power']
                p_min_percent = item['min_watt_in_percent']
                results_device_type = item['name_device_type']
                if p_max and p_min_percent:
                    p_min = (p_max*p_min_percent)/100
                # Check device On/Off
                value_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ControlINV"]
                if value_array:
                    value = value_array[0]
                else:
                    continue
                # Check device Fault
                operator_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
                if operator_array:
                    operator = operator_array[0]
                else:
                    continue
                # Get Slope Power Limit 
                slope_array = [field["slope"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "WMax"]
                if slope_array:
                    slope = slope_array[0]
                else:
                    continue
                # device is inv , online , auto , not fault => control 
                if results_device_type == "PV System Inverter" and status_device == 'online' and mode == 1 and operator not in [7, 8]:
                    # create list sent mqtt 
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
    gIntValueTotalPowerInInvInAutoMode = sum(device['p_max'] for device in ArayyDeviceList)
    return ArayyDeviceList
############################################################################ List Device Systemp ############################################################################
# Describe getListALLInvInProject 
# 	 * @description getListALLInvInProject
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
async def getListALLInvInProject(messageAllDevice, StringSerialNumerInTableProjectSetup, host, port, username, password):
    # Global variables
    global gIntValueTotalPowerInInvInAutoMode, MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS,gIntValueConsumptionSystemp,\
    gIntValueProductionSystemp,gIntValuePowerLimit,gFloatValueSystemPerformance,gIntValueSettingArlamLowPerformance , \
    gIntValueSettingArlamHighPerformance ,gIntValueTotalPowerInInvInManMode,gIntValueTotalPowerInALLInv,gStringModeSystempCurrent
    
    # Local variable
    ArrayDeviceList = []
    ArrayOperator = []
    ArrayWmax = []
    ArrayCapacitypower = []
    ArrayRealpower = []
    intOperator = 0
    stringOperatorText = ""
    floatWmax = 0.0
    floatCapacitypower = 0.0
    floatRealpower = 0.0
    timeStampGetList = get_utc()
    StringMessageStatusSystemPerformance = ''
    intStatusSystemPerformance = 0
    gIntValueTotalPowerInInvInManModeTemp = 0
    # Get result mqtt 
    if messageAllDevice and isinstance(messageAllDevice, list):
        for item in messageAllDevice:
            # get info about device
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                status_device = item['status_device']
                if item['rated_power_custom'] != None :
                    p_max_custom = item['rated_power_custom']
                else:
                    p_max_custom = item['rated_power']
                p_min_percent = item['min_watt_in_percent']
                device_name = item['device_name']
                results_device_type = item['name_device_type']
                # check device is inv
                if results_device_type == "PV System Inverter":
                    # get info list device
                    stringOperatorText = {
                        0: "shutting down",
                        1: "shutting down",
                        4: "running",
                        5: "running",  
                        6: "shutting down",
                        7: "fault",
                    }
                    ArrayOperator = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
                    intOperator = ArrayOperator[0] if ArrayOperator else 0
                    stringOperatorText = stringOperatorText.get(intOperator, "off")
                    
                    ArrayWmax = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "WMax"]
                    floatWmax = ArrayWmax[0] if ArrayWmax else 0
                    
                    ArrayCapacitypower = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "PowerOutputCapability"]
                    floatCapacitypower = ArrayCapacitypower[0] if ArrayCapacitypower else 0
                    
                    if floatWmax != None :
                        if gStringModeSysTemp != 1:
                            if mode == 0:
                                gIntValueTotalPowerInInvInManModeTemp += floatWmax
                            else:
                                gIntValueTotalPowerInInvInManModeTemp += 0
                            gIntValueTotalPowerInInvInManMode = gIntValueTotalPowerInInvInManModeTemp
                        else:
                            gIntValueTotalPowerInInvInManMode = 0
                        
                    ArrayRealpower = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
                    floatRealpower = ArrayRealpower[0] if ArrayRealpower else 0
                    # device offline   
                    if status_device == 'offline':
                        floatRealpower = 0.0
                        stringOperatorText = "off"
                    # Calculate pmin   
                    if p_max_custom and p_min_percent:
                        p_min = round((p_max_custom * p_min_percent) / 100, 4)
                    else:
                        p_min = 0.0
                    # create list sent mqtt
                    ArrayDeviceList.append({
                        'id_device': id_device,
                        'device_name': device_name,
                        'mode': mode,
                        'status_device': status_device,
                        'operator': stringOperatorText,
                        'capacitypower': floatCapacitypower,
                        'p_max': p_max_custom,
                        'p_min': p_min,
                        'wmax': floatWmax,
                        'realpower': floatRealpower,
                        'timestamp': timeStampGetList,
                    })
    if gFloatValueSystemPerformance < gIntValueSettingArlamLowPerformance:
        StringMessageStatusSystemPerformance = "System performance is below expectations."
        intStatusSystemPerformance = 0
    elif gIntValueSettingArlamLowPerformance <= gFloatValueSystemPerformance < gIntValueSettingArlamHighPerformance:
        StringMessageStatusSystemPerformance = "System performance is meeting"
        intStatusSystemPerformance = 1
    else:
        StringMessageStatusSystemPerformance = "System performance is exceeding established thresholds."
        intStatusSystemPerformance = 2
    # Caculator gFloatValueSystemPerformance
    if gStringModeSystempCurrent == 0:
        if gIntValueTotalPowerInALLInv :
            gFloatValueSystemPerformance = (gIntValueProductionSystemp /gIntValueTotalPowerInALLInv) * 100
        else:
            gFloatValueSystemPerformance = 0
        
    gFloatValueSystemPerformance = round(gFloatValueSystemPerformance, 1)
    
    gIntValueTotalPowerInInvInAutoMode = round(gIntValueTotalPowerInInvInAutoMode, 3)
    gIntValueTotalPowerInInvInManModeTemp = round(gIntValueTotalPowerInInvInManModeTemp,1)
    
    gIntValueTotalPowerInALLInv = gIntValueTotalPowerInInvInAutoMode + gIntValueTotalPowerInInvInManModeTemp
    
    result = {
    "ModeSystempCurrent":gStringModeSystempCurrent,
    "devices": ArrayDeviceList,
    "total_max_power": gIntValueTotalPowerInALLInv,
    "system_performance": {
        "performance": gFloatValueSystemPerformance,
        "message": StringMessageStatusSystemPerformance,
        "status": intStatusSystemPerformance
    }
    }
    mqtt_public_paho_zip(host, port, StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS, username, password, result)
    push_data_to_mqtt(host, port, StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS + "Binh", username, password, result)
    return ArrayDeviceList
# Describe getValueProductionAndConsumtion 
# 	 * @description getValueProductionAndConsumtion
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return value_production ,value_consumption
# 	 */ 
############################################################################ Get Value Metter ############################################################################
async def getValueProductionAndConsumtion():
    # Global variables
    global gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp ,gIntValueProduction1Minute,\
    gIntValueConsumption1Minute,gIntValueProduction1Hour, gIntValueConsumption1Hour,gIntValueProductionDaily,gIntValueConsumptionDaily, \
    start_time_hourly , start_time_daily ,start_time_minutely,gIntValueConsumtionInModeZeroExport,gIntValueConsumtionInModePowerLimit,\
    gIntValueProductionInModePowerLimit,gIntValueProductionInModeZeroExport,cycle_time1s,gIntControlModeDetail
    # Local variables
    ArrayValueProduction = []
    ArrayValueConsumtion = []
    IntTotalValueProduction = 0
    IntTotalValueConsumtion = 0
    IntIntegralValueProduction = 0
    IntIntegralValueConsumtion = 0
    last_update_time = start_time_minutely
    last_update_time_production = start_time_minutely
    current_time = time.time()
    # Get Topic /Devices/All
    if gArrayMessageAllDevice:
        for item in gArrayMessageAllDevice:
            if 'id_device' in item:
                id_device = item['id_device']
                # Select type Meter
                result_type_meter = MySQL_Select("SELECT `device_type`.`name` FROM `device_type` INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id WHERE `device_list`.id = %s", (id_device,))
                # Caculator Value Meter Production
                if result_type_meter:
                    if result_type_meter[0]["name"] == "PV System Inverter": 
                        ArrayValueProduction = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
                        if len(ArrayValueProduction) > 0 and ArrayValueProduction[0] is not None:
                            IntTotalValueProduction += ArrayValueProduction[0]
                            gIntValueProductionSystemp = IntTotalValueProduction
                            dt = current_time - last_update_time_production
                            IntIntegralValueProduction += gIntValueProductionSystemp * dt/3600
                            last_update_time_production = current_time
                    # Caculator Value Meter Consumption
                    elif result_type_meter[0]["name"] == "Consumption meter":
                        ArrayValueConsumtion = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
                        if len(ArrayValueConsumtion) > 0 and ArrayValueConsumtion[0] is not None:
                            IntTotalValueConsumtion += ArrayValueConsumtion[0]
                            gIntValueConsumptionSystemp = IntTotalValueConsumtion
                            dt = current_time - last_update_time
                            IntIntegralValueConsumtion += gIntValueConsumptionSystemp * dt/3600 
                            last_update_time = current_time
                # Check if 1 hour has passed and Reset variable
                current_second = int(current_time // 1) 
                current_minute = int(current_time // 60)
                current_hour = int(current_time // 3600)
                current_day = int(current_time // (3600 * 24))
                # total value of power consumption and production power in power limit and zero export mode
                if current_second != int(cycle_time1s):
                    dts = current_time - cycle_time1s
                    
                    if gIntControlModeDetail == 1:
                        gIntValueProductionInModeZeroExport += gIntValueProductionSystemp * dts / 3600
                        gIntValueConsumtionInModeZeroExport += gIntValueConsumptionSystemp * dts / 3600
                        gIntValueProductionInModePowerLimit = 0
                        gIntValueConsumtionInModePowerLimit = 0
                        
                    elif gIntControlModeDetail == 2:
                        gIntValueProductionInModePowerLimit += gIntValueProductionSystemp * dts / 3600
                        gIntValueConsumtionInModePowerLimit += gIntValueConsumptionSystemp * dts / 3600
                        gIntValueProductionInModeZeroExport = 0
                        gIntValueConsumtionInModeZeroExport = 0
                        
                    elif current_hour == 0 and current_minute == 0 and current_second == 0:
                        gIntValueProductionInModeZeroExport = 0
                        gIntValueConsumtionInModeZeroExport = 0
                        gIntValueProductionInModePowerLimit = 0
                        gIntValueConsumtionInModePowerLimit = 0
                    
                    cycle_time1s = current_time
                # Caculator powwer for 1 minute
                if current_minute != int(start_time_minutely // 60):
                    gIntValueProduction1Minute = round(IntIntegralValueProduction)
                    gIntValueConsumption1Minute = round(gIntValueConsumptionSystemp)
                    IntIntegralValueProduction = 0
                    gIntValueConsumptionSystemp = 0
                    gIntValueProduction1Hour += gIntValueProduction1Minute
                    gIntValueConsumption1Hour += gIntValueConsumption1Minute
                    gIntValueProductionDaily += gIntValueProduction1Minute
                    gIntValueConsumptionDaily += gIntValueConsumption1Minute
                    start_time_minutely = current_time
                # Caculator powwer for 1 hour
                if current_hour != int(start_time_hourly // 3600):
                    gIntValueProduction1Hour = 0
                    gIntValueConsumption1Hour = 0
                    start_time_hourly = current_time
                # Caculator powwer for 1 day
                if current_day != int(start_time_daily // (3600 * 24)):
                    gIntValueProductionDaily = 0
                    gIntValueConsumptionDaily = 0
                    start_time_daily = current_time   
# Describe pudValueProductionAndConsumtionInMQTT 
# 	 * @description pudValueProductionAndConsumtionInMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return value_meter push mqtt 
# 	 */ 
async def pudValueProductionAndConsumtionInMQTT(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    # Global variables
    global gArrayMessageAllDevice, gIntValueProductionSystemp, gIntValueConsumptionSystemp, gIntValueProduction1Minute , \
    gIntValueConsumption1Minute, gIntValueProduction1Hour, gIntValueConsumption1Hour, gIntValueProductionDaily, gIntValueConsumptionDaily,\
    MQTT_TOPIC_PUD_MONIT_METER,gIntValueConsumtionInModePowerLimit,gIntValueProductionInModePowerLimit,gIntValueConsumtionInModeZeroExport,\
    gIntValueProductionInModeZeroExport,gFloatValueMaxPredictProductionInstant
    
    try:
        timeStampGetValueProductionAndConsumtion = get_utc()
        topicPublicValueProductionAndConsumtion = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_MONIT_METER
        gFloatValueMaxPredictProductionInstant_temp = 0
        # Format data
        ValueProductionAndConsumtion = {
            "Timestamp": timeStampGetValueProductionAndConsumtion,
            "instant": {},
            "minutely": {},
            "hourly": {},
            "daily": {},
            "zero_export": {},
            "power_limit": {},
        }

        if gArrayMessageAllDevice:
            # await getValueProductionAndConsumtion_zero_export()
            for device in gArrayMessageAllDevice:
                if "mppt" in device:
                    for mppt in device["mppt"]:
                        if "power" in mppt:
                            gFloatValueMaxPredictProductionInstant_temp += mppt["power"]
                            gFloatValueMaxPredictProductionInstant = gFloatValueMaxPredictProductionInstant_temp

        # instant power
        ValueProductionAndConsumtion["instant"]["production"] = round(gIntValueProductionSystemp , 4)
        ValueProductionAndConsumtion["instant"]["consumption"] = round(gIntValueConsumptionSystemp , 4)
        ValueProductionAndConsumtion["instant"]["grid_feed"] = round((gIntValueProductionSystemp - gIntValueConsumptionSystemp), 4)
        ValueProductionAndConsumtion["instant"]["max_production"] = round(gFloatValueMaxPredictProductionInstant , 4)

        # minutely power
        ValueProductionAndConsumtion["minutely"]["production"] = round(gIntValueProduction1Minute , 4)
        ValueProductionAndConsumtion["minutely"]["consumption"] = round(gIntValueConsumption1Minute , 4)
        ValueProductionAndConsumtion["minutely"]["grid_feed"] = round((gIntValueProduction1Minute - gIntValueConsumption1Minute), 4)

        # hourly power
        ValueProductionAndConsumtion["hourly"]["production"] = round(gIntValueProduction1Hour , 4)
        ValueProductionAndConsumtion["hourly"]["consumption"] = round(gIntValueConsumption1Hour , 4)
        ValueProductionAndConsumtion["hourly"]["grid_feed"] = round((gIntValueProduction1Hour - gIntValueConsumption1Hour), 4)

        # daily power
        ValueProductionAndConsumtion["daily"]["production"] = round(gIntValueProductionDaily , 4)
        ValueProductionAndConsumtion["daily"]["consumption"] = round(gIntValueConsumptionDaily, 4)
        ValueProductionAndConsumtion["daily"]["grid_feed"] = round((gIntValueProductionDaily - gIntValueConsumptionDaily) , 4)

        # power limit 
        ValueProductionAndConsumtion["zero_export"]["totalproduction"] = round(gIntValueProductionInModeZeroExport , 4)
        ValueProductionAndConsumtion["zero_export"]["totalconsumption"] = round(gIntValueConsumtionInModeZeroExport , 4)
        ValueProductionAndConsumtion["zero_export"]["differential"] = round((gIntValueConsumtionInModeZeroExport - gIntValueProductionInModeZeroExport) , 4)

        # power zero export 
        ValueProductionAndConsumtion["power_limit"]["totalproduction"] = round(gIntValueProductionInModePowerLimit , 4)
        ValueProductionAndConsumtion["power_limit"]["totalconsumption"] = round(gIntValueConsumtionInModePowerLimit , 4)
        ValueProductionAndConsumtion["power_limit"]["differential"] = round((gIntValueProductionInModePowerLimit - gIntValueConsumtionInModePowerLimit), 4)
        
        # Push system_info to MQTT
        mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublicValueProductionAndConsumtion, mqtt_username, mqtt_password, ValueProductionAndConsumtion)
    except Exception as err:
        print(f"Error MQTT subscribe pudValueProductionAndConsumtionInMQTT: '{err}'")
############################################################################ Power Limit Control  ############################################################################
# Describe processCaculatorPowerForInvInPowerLimitMode 
# 	 * @description processCaculatorPowerForInvInPowerLimitMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return gIntValuePowerForEachInvInModePowerLimit
# 	 */ 
async def processCaculatorPowerForInvInPowerLimitMode(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    # Global variables
    global gArrayMessageAllDevice, gIntValuePowerLimit, gArraydevices, gIntValueProductionSystemp, gIntValueTotalPowerInInvInAutoMode,\
    MQTT_TOPIC_PUD_CONTROL_AUTO, gIntValuePowerForEachInvInModePowerLimit,gStringModeSystempCurrent,gFloatValueSystemPerformance,\
    gIntValueTotalPowerInInvInManMode,gBitManWrite
    # Local variables
    intPowerMaxOfInv = 0
    intPowerMinOfInv = 0
    
    processCaculatorPowerForInvInPowerLimitMode = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CONTROL_AUTO
    # Check device equipment qualified for control
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
        print("device",gArraydevices)
    if gIntValuePowerLimit > 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = (gIntValueProductionSystemp /gIntValuePowerLimit) * 100
    elif gIntValueConsumptionSystemp <= 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = 101
    else:
        gFloatValueSystemPerformance = 0
        
    # get information about power in database and varaable gArraydevices
    if gArraydevices:
        listInvControlPowerLimitMode = []
        for device in gArraydevices:
            id_device = device["id_device"]
            mode = device["mode"]
            intPowerMaxOfInv = device["p_max"]
            intPowerMaxOfInv = float(intPowerMaxOfInv)
            intPowerMinOfInv = device["p_min"]
            intPowerMinOfInv = float(intPowerMinOfInv)
            # Convert power real 
            if intPowerMaxOfInv :
                if gStringModeSystempCurrent == 1:
                    floatEfficiencySystemp = ((gIntValuePowerLimit)/gIntValueTotalPowerInInvInAutoMode)
                else:
                    floatEfficiencySystemp = ((gIntValuePowerLimit-gIntValueTotalPowerInInvInManMode)/gIntValueTotalPowerInInvInAutoMode)
                # Calculate power value according to total system performance
                if 0 <= floatEfficiencySystemp <= 1:
                    gIntValuePowerForEachInvInModePowerLimit = (floatEfficiencySystemp * intPowerMaxOfInv)
                elif floatEfficiencySystemp < 0:
                    gIntValuePowerForEachInvInModePowerLimit = 0
                else:
                    gIntValuePowerForEachInvInModePowerLimit = intPowerMaxOfInv

            # If the total capacity produced has not reached the set value, proceed
            if gIntValueProductionSystemp < gIntValuePowerLimit:
                if device['controlinv'] == 1: # Check device is off , on device 
                    ItemlistInvControlPowerLimitMode = {
                        "id_device": id_device,
                        "mode": mode,
                        "time": get_utc(),
                        "status": "power limit",
                        "setpoint": gIntValuePowerLimit - gIntValueTotalPowerInInvInManMode ,
                        "feedback": gIntValueProductionSystemp,
                        "parameter": [
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModePowerLimit}
                        ]
                    }
                elif device['controlinv'] == 0:
                    ItemlistInvControlPowerLimitMode = {
                        "id_device": id_device,
                        "mode": mode,
                        "time": get_utc(),
                        "status": "power limit",
                        "setpoint": gIntValuePowerLimit - gIntValueTotalPowerInInvInManMode,
                        "feedback": gIntValueProductionSystemp,
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModePowerLimit}
                        ]
                    }
            else:
                ItemlistInvControlPowerLimitMode = {
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
            # Accumulate devices that are eligible to run automatically to push to mqtt
            listInvControlPowerLimitMode.append(ItemlistInvControlPowerLimitMode)
        if len(gArraydevices) == len(listInvControlPowerLimitMode) and gBitManWrite == 0:
            print("gBitManWrite",gBitManWrite)
            print("Value Power Limit ", gIntValuePowerLimit)
            print("Value Power Man  ", gIntValueTotalPowerInInvInManMode)
            mqtt_public_paho_zip(mqtt_host, mqtt_port, processCaculatorPowerForInvInPowerLimitMode, mqtt_username, mqtt_password, listInvControlPowerLimitMode)
            push_data_to_mqtt(mqtt_host, mqtt_port, processCaculatorPowerForInvInPowerLimitMode + "Binh", mqtt_username, mqtt_password, listInvControlPowerLimitMode)
            gIntValuePowerForEachInvInModePowerLimit = 0
############################################################################ Zero Export Control ############################################################################
# Describe processCaculatorPowerForInvInZeroExportMode 
# 	 * @description processCaculatorPowerForInvInZeroExportMode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return gIntValuePowerForEachInvInModeZeroExport
# 	 */ 
async def processCaculatorPowerForInvInZeroExportMode(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    # Global variables
    global gArrayMessageAllDevice ,gIntValueThresholdZeroExport ,gIntValueOffsetZeroExport , gIntValueConsumptionSystemp , gArraydevices ,\
    gIntValueProductionSystemp ,gIntValueTotalPowerInInvInAutoMode ,MQTT_TOPIC_PUD_CONTROL_AUTO,gIntValuePowerForEachInvInModeZeroExport,\
    gListMovingAverageConsumption,gIntValueTotalPowerInInvInManMode,gStringModeSystempCurrent,gFloatValueSystemPerformance,gBitManWrite
    # Local variables
    floatEfficiencySystemp = 0
    id_device = 0
    intPowerMaxOfInv = 0
    setpointCalculatorPowerForEachInv = 0
    topicPudCaculatorPowerForInvInZeroExportMode = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CONTROL_AUTO
    if gIntValueConsumptionSystemp :
        # Calculate the moving average, the number of times declared at the beginning of the program
        if gStringModeSystempCurrent == 1:
            gListMovingAverageConsumption.append(gIntValueConsumptionSystemp)
        else:
            gListMovingAverageConsumption.append(gIntValueConsumptionSystemp-gIntValueTotalPowerInInvInManMode)
            
        if gIntValueConsumptionSystemp > gIntValueTotalPowerInInvInManMode:
            intAvgValueComsumtion = sum(gListMovingAverageConsumption) / len(gListMovingAverageConsumption)
            intAvgValueComsumtion
        else:
            intAvgValueComsumtion = 0

        # Limit the change in setpoint
        if not hasattr(processCaculatorPowerForInvInZeroExportMode, 'last_setpoint'):
            processCaculatorPowerForInvInZeroExportMode.last_setpoint = intAvgValueComsumtion
        new_setpoint = intAvgValueComsumtion
        setpointCalculatorPowerForEachInv = max(
            processCaculatorPowerForInvInZeroExportMode.last_setpoint - gMaxValueChangeSetpoint,
            min(processCaculatorPowerForInvInZeroExportMode.last_setpoint + gMaxValueChangeSetpoint, new_setpoint)
        )
        processCaculatorPowerForInvInZeroExportMode.last_setpoint = setpointCalculatorPowerForEachInv
        if setpointCalculatorPowerForEachInv:
            setpointCalculatorPowerForEachInv -= setpointCalculatorPowerForEachInv * gIntValueOffsetZeroExport / 100
        if gIntValueProductionSystemp > gIntValueConsumptionSystemp:
            setpointCalculatorPowerForEachInv -= (gIntValueProductionSystemp - gIntValueConsumptionSystemp)
        setpointCalculatorPowerForEachInv = round(setpointCalculatorPowerForEachInv, 4)
    # Check device equipment qualified for control
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
        print("Device List", gArraydevices)
    if gIntValueConsumptionSystemp > 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = (gIntValueProductionSystemp /gIntValueConsumptionSystemp) * 100
    elif gIntValueConsumptionSystemp <= 0 and gIntValueProductionSystemp > 0:
        gFloatValueSystemPerformance = 101
    else :
        gFloatValueSystemPerformance = 0
    
    # Get information about power in database and variable devices
    if gArraydevices:
        listInvControlZeroExportMode = []
        for device in gArraydevices:
            id_device = device["id_device"]
            mode = device["mode"]
            intPowerMaxOfInv = float(device["p_max"])
            # Calculate the total performance of the system
            if setpointCalculatorPowerForEachInv and intPowerMaxOfInv :
                floatEfficiencySystemp = (min(setpointCalculatorPowerForEachInv,gIntValueConsumptionSystemp) / gIntValueTotalPowerInInvInAutoMode)
                # Calculate the performance for each device based on the total performance
                if floatEfficiencySystemp:
                    gIntValuePowerForEachInvInModeZeroExport = floatEfficiencySystemp * intPowerMaxOfInv
                # Calculate power value according to total system performance
                if 0 <= floatEfficiencySystemp <= 1:
                    gIntValuePowerForEachInvInModeZeroExport = floatEfficiencySystemp * intPowerMaxOfInv
                elif floatEfficiencySystemp < 0:
                    gIntValuePowerForEachInvInModeZeroExport = 0 
                else:
                    gIntValuePowerForEachInvInModeZeroExport = intPowerMaxOfInv 
                    
            if (gIntValueConsumptionSystemp >= gIntValueThresholdZeroExport) and (gIntValueConsumptionSystemp >= 0):
                # Check device is off, on device
                if device['controlinv'] == 1:
                    ItemlistInvControlPowerLimitMode = {
                        "id_device": id_device,
                        "Mode": "Add",
                        "mode": mode,
                        "time": get_utc(),
                        "status": "zero export",
                        "setpoint": setpointCalculatorPowerForEachInv,
                        "parameter": [
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModeZeroExport}
                        ]
                    }
                elif device['controlinv'] == 0:
                    ItemlistInvControlPowerLimitMode = {
                        "id_device": id_device,
                        "Mode": "Add",
                        "mode": mode,
                        "status": "zero export",
                        "setpoint": setpointCalculatorPowerForEachInv,
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModeZeroExport}
                        ]
                    }
            else:
                ItemlistInvControlPowerLimitMode = {
                        "id_device": id_device,
                        "Mode": "Add",
                        "mode": mode,
                        "status": "zero export",
                        "setpoint": setpointCalculatorPowerForEachInv,
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": 0}
                        ]
                    }
            listInvControlZeroExportMode.append(ItemlistInvControlPowerLimitMode)
        # Push data to MQTT
        if len(gArraydevices) == len(listInvControlZeroExportMode) and gBitManWrite == 0:
            print("gBitManWrite",gBitManWrite)
            print("Value ZeroExport ", setpointCalculatorPowerForEachInv)
            print("Value Power Man  ", gIntValueTotalPowerInInvInManMode)
            mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPudCaculatorPowerForInvInZeroExportMode, mqtt_username, mqtt_password, listInvControlZeroExportMode)
            push_data_to_mqtt(mqtt_host, mqtt_port, topicPudCaculatorPowerForInvInZeroExportMode + "Binh", mqtt_username, mqtt_password, listInvControlZeroExportMode)
            gIntValuePowerForEachInvInModeZeroExport = 0
# Describe processNonExportPowerLimit 
# 	 * @description processNonExportPowerLimit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return power_max
# 	 */ 
async def processNonExportPowerLimit(StringSerialNumerInTableProjectSetup, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    # Global variables
    global gArrayMessageAllDevice , gArraydevices ,MQTT_TOPIC_PUD_CONTROL_AUTO
    # Local variables
    intPowerMaxOfInv = 0
    floatCoefficientConvertedValueForINV = 1.0
    topicPudprocessNonExportPowerLimit = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CONTROL_AUTO
    gIntValuePowerForEachInvInModeNoneAuto = 0
    # Check device equipment qualified for control
    if gArrayMessageAllDevice:
        gArraydevices = await getListDeviceAutoModeInALLInv(gArrayMessageAllDevice)
    # get information about power in database and varable gArraydevices
    if gArraydevices :
            listInvControlNonAutoMode = []
            for device in gArraydevices:
                id_device = device["id_device"]
                mode = device["mode"]
                intPowerMaxOfInv = device["p_max"]
                intPowerMaxOfInv = float(intPowerMaxOfInv)
                intPowerMinOfInv = device["p_min"]
                intPowerMinOfInv = float(intPowerMinOfInv)
                floatCoefficientConvertedValueForINV = device["slope"]
                # Convert power max real 
                if intPowerMaxOfInv and floatCoefficientConvertedValueForINV :
                    gIntValuePowerForEachInvInModeNoneAuto = intPowerMinOfInv/floatCoefficientConvertedValueForINV
                # Check device is off , on device 
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": id_device,
                        "mode": mode,
                        "status": "Pmin",
                        "parameter": [
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModeNoneAuto}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": id_device,
                        "mode": mode,
                        "status": "Pmin",
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": gIntValuePowerForEachInvInModeNoneAuto}
                        ]
                    }
                listInvControlNonAutoMode.append(new_device)
            # Push data to mqtt 
            if len(gArraydevices) == len(listInvControlNonAutoMode):
                mqtt_public_paho_zip( mqtt_host, mqtt_port, topicPudprocessNonExportPowerLimit, mqtt_username, mqtt_password, listInvControlNonAutoMode)
############################################################################ Setup Parameter Control ############################################################################
# Describe processUpdateParameterModeDetail 
# 	 * @description processUpdateParameterModeDetail
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password}
# 	 * @return MySQL_Update gIntValueOffsetZeroExport,gIntValuePowerLimit,gIntValueOffsetPowerLimit
# 	 */ 
async def processUpdateParameterModeDetail(messageParameterControlAuto,StringSerialNumerInTableProjectSetup, mqtt_host ,mqtt_port, \
    mqtt_username,mqtt_password ):
    # Global variables
    global gIntValueThresholdZeroExport,gIntValueOffsetZeroExport,gIntValuePowerLimit,gIntValueOffsetPowerLimit,\
    MQTT_TOPIC_PUD_CHOICES_MODE_AUTO,gIntValueTotalPowerInInvInAutoMode,gIntValueTotalPowerInALLInv
    
    # Local variables
    topicPudUpdateParameterModeDetail = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
    timeStamp = get_utc()
    stringAutoMode = ""
    intComment = 0
    gIntValueOffsetZeroExport_temp = 0
    gIntValueThresholdZeroExport_temp = 0
    gIntValuePowerLimit_temp = 0
    gIntValueOffsetPowerLimit_temp = 0
    arrayResultUpdateParameterZeroExportInTableProjectSetUp = []
    arrayResultUpdateParameterPowerLimitInTableProjectSetUp = []
    # Receve data from mqtt
    try:
        if messageParameterControlAuto and 'mode' in messageParameterControlAuto and 'offset' in messageParameterControlAuto:
            stringAutoMode = messageParameterControlAuto['mode'] 
            stringAutoMode = int(stringAutoMode)
            # Compare get information update database 
            if stringAutoMode == 1:
                gIntValueOffsetZeroExport_temp = messageParameterControlAuto["offset"]
                if gIntValueOffsetZeroExport_temp is None:
                    pass
                else :
                    gIntValueOffsetZeroExport = gIntValueOffsetZeroExport_temp
                gIntValueThresholdZeroExport_temp = messageParameterControlAuto["threshold"]
                if gIntValueThresholdZeroExport_temp is None:
                    pass
                else :
                    gIntValueThresholdZeroExport = gIntValueThresholdZeroExport_temp
                arrayResultUpdateParameterZeroExportInTableProjectSetUp = MySQL_Update_V1("update project_setup set value_offset_zero_export = %s,threshold_zero_export = %s", (gIntValueOffsetZeroExport,gIntValueThresholdZeroExport,))
            elif stringAutoMode == 2:
                gIntValueOffsetPowerLimit_temp = messageParameterControlAuto["offset"]
                if gIntValueOffsetPowerLimit_temp is None:
                    pass
                else :
                    gIntValueOffsetPowerLimit = gIntValueOffsetPowerLimit_temp
                gIntValuePowerLimit_temp = messageParameterControlAuto["value"]
                if gIntValuePowerLimit_temp is not None :
                    if gIntValuePowerLimit_temp <= gIntValueTotalPowerInALLInv:
                        gIntValuePowerLimit = gIntValuePowerLimit_temp
                        # write information in database 
                        if gIntValuePowerLimit <= gIntValueTotalPowerInALLInv:
                            arrayResultUpdateParameterPowerLimitInTableProjectSetUp = MySQL_Update_V1("update project_setup set value_power_limit = %s ,value_offset_power_limit = %s ", (gIntValuePowerLimit_temp,gIntValueOffsetPowerLimit,))
                        # convert value kw to w 
                            gIntValuePowerLimit = (gIntValuePowerLimit - (gIntValuePowerLimit*gIntValueOffsetPowerLimit)/100)
            # When you receive one of the above information, give feedback to mqtt
            print("arrayResultUpdateParameterZeroExportInTableProjectSetUp",arrayResultUpdateParameterZeroExportInTableProjectSetUp)
            print("arrayResultUpdateParameterPowerLimitInTableProjectSetUp",arrayResultUpdateParameterPowerLimitInTableProjectSetUp)
            print("gIntValuePowerLimit_temp",gIntValuePowerLimit_temp)
            print("gIntValuePowerLimit_temp",gIntValuePowerLimit_temp)
            print("gIntValueTotalPowerInALLInv",gIntValueTotalPowerInALLInv)
            
            if arrayResultUpdateParameterZeroExportInTableProjectSetUp == None or arrayResultUpdateParameterPowerLimitInTableProjectSetUp == None or (gIntValuePowerLimit_temp != None and gIntValuePowerLimit_temp > gIntValueTotalPowerInALLInv):
                intComment = 400 
            else:
                intComment = 200 
            objectSend = {
                        "time_stamp" :timeStamp,
                        "status":intComment, 
                        }
            mqtt_public_paho_zip(mqtt_host,
                    mqtt_port,
                    topicPudUpdateParameterModeDetail ,
                    mqtt_username,
                    mqtt_password,
                    objectSend)
            push_data_to_mqtt(mqtt_host,
                    mqtt_port,
                    topicPudUpdateParameterModeDetail + "Binh" ,
                    mqtt_username,
                    mqtt_password,
                    objectSend)
            
    except Exception as err:
        print(f"Error MQTT subscribe processUpdateParameterModeDetail: '{err}'")
# Describe processUpdateModeDetail 
# 	 * @description processUpdateModeDetail
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,StringSerialNumerInTableProjectSetup, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password}
# 	 * @return MySQL_Update enable_zero_export ,enable_power_limit
# 	 */ 
async def processUpdateModeDetail(messageModeControlAuto,StringSerialNumerInTableProjectSetup, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password ):
    # Global variables
    global gIntControlModeDetail,MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK
    # Local variables
    topicPudModeDetail = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_PUD_CHOICES_MODE_AUTO_DETAIL_FEEDBACK
    timeStamp = get_utc()
    stringAutoMode = ""
    intComment = 0
    arrayResultUpdateModeDetailInTableProjectSetUp = []
    # Receve data from mqtt
    try:
        if messageModeControlAuto and 'control_mode' in messageModeControlAuto :
            stringAutoMode = messageModeControlAuto['control_mode'] 
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
                        }
            mqtt_public_paho_zip(mqtt_host,
                    mqtt_port,
                    topicPudModeDetail ,
                    mqtt_username,
                    mqtt_password,
                    objectSend)
        else:
            pass
            
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
    Kp,Ki,Kd,dt,gIntValueSettingArlamLowPerformance,gIntValueSettingArlamHighPerformance
    # Local variables
    gIntValuePowerLimit_temp = 0
    arrayResultInitializeParameterZeroExportInTableProjectSetUp = []
    # Get database information the first time
    try:
        arrayResultInitializeParameterZeroExportInTableProjectSetUp = await MySQL_Select_v1("select * from project_setup")
        if arrayResultInitializeParameterZeroExportInTableProjectSetUp:
            gIntControlModeDetail = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["control_mode"]
            gIntValueOffsetZeroExport = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_zero_export"]
            gIntValuePowerLimit_temp = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_power_limit"]
            gIntValueOffsetPowerLimit = arrayResultInitializeParameterZeroExportInTableProjectSetUp[0]["value_offset_power_limit"]
            gIntValuePowerLimit = (gIntValuePowerLimit_temp - (gIntValuePowerLimit_temp*gIntValueOffsetPowerLimit)/100)
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
async def selectAutoModeDetail(StringSerialNumerInTableProjectSetup,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password):
    # Global variables 
    global gIntControlModeDetail
    # await waitting_process_man()
    # Select the auto run process
    if gIntControlModeDetail == 1 :
        print("==============================zero_export==============================")
        await processCaculatorPowerForInvInZeroExportMode(StringSerialNumerInTableProjectSetup,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    elif gIntControlModeDetail == 2 :
        print("==============================power_limit==============================")
        await processCaculatorPowerForInvInPowerLimitMode(StringSerialNumerInTableProjectSetup,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    else :
        print("=======================power_min========================")
        await processNonExportPowerLimit(StringSerialNumerInTableProjectSetup,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
# Describe process_zero_export_power_limit 
# 	 * @description process_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return chosse process zero_export ,power_limit ,zero_export + power_limit , Auto - Full P

############################################################################ Sud MQTT ############################################################################
# Describe processMessage 
# 	 * @description pudSystempModeTrigerEachDeviceChange
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,StringSerialNumerInTableProjectSetup, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def processMessage(topic, message,StringSerialNumerInTableProjectSetup, host, port, username, password):
    global MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    global MQTT_TOPIC_SUD_MODEGET_INFORMATION
    global MQTT_TOPIC_SUD_CHOICES_MODE_AUTO
    global MQTT_TOPIC_SUD_DEVICES_ALL
    global MQTT_TOPIC_SUD_MODEGET_CPU
    global MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE
    global MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL
    global MQTT_TOPIC_SUD_SETTING_ARLAM
    global MQTT_TOPIC_SUD_MODIFY_DEVICE
    global MQTT_TOPIC_SUD_FEEDBACK_WRITE

    result_topic2 = ""
    result_topic3 = ""
    # result_topic5 = ""
    result_topic6 = ""
    result_topic7 = ""
    result_topic8 = ""
    # result_topic9 = ""
    
    global gArrayMessageAllDevice
    global gArrayMessageChangeModeSystemp
    global gBitManWrite
    
    topic1 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    topic2 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_MODEGET_INFORMATION
    topic3 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_CHOICES_MODE_AUTO
    topic4 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_DEVICES_ALL
    # topic5 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_MODEGET_CPU
    topic6 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE
    topic7 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL
    topic8 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_CONTROL_MAN
    topic9 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_MODIFY_DEVICE
    # topic10 = StringSerialNumerInTableProjectSetup + MQTT_TOPIC_SUD_FEEDBACK_WRITE
    try:
        if topic == topic1:
            gArrayMessageChangeModeSystemp = message
            await subSystempModeWhenUserChangeModeSystemp (StringSerialNumerInTableProjectSetup, host, port, username, password)
            print("gArrayMessageChangeModeSystemp",gArrayMessageChangeModeSystemp)
        elif topic == topic2:
            result_topic2 = message
            await pudInformationProjectSetupWhenRequest(result_topic2,StringSerialNumerInTableProjectSetup, host, port, username, password)
            print("result_topic2",result_topic2)
        elif topic == topic3:
            result_topic3 = message
            await processUpdateParameterModeDetail(result_topic3,StringSerialNumerInTableProjectSetup,host, port, username, password)
            print("result_topic3",result_topic3)
        elif topic == topic4:
            gArrayMessageAllDevice = message
            await getListALLInvInProject(gArrayMessageAllDevice,StringSerialNumerInTableProjectSetup, host, port, username, password)
        # elif topic == topic5:
        #     result_topic5 = message
        #     print("result_topic5",result_topic5)
        elif topic == topic6:
            result_topic6 = message
            await insertInformationProjectSetupWhenRequest(result_topic6,StringSerialNumerInTableProjectSetup, host, port, username, password)
            print("result_topic6",result_topic6)
        elif topic == topic7:
            result_topic7 = message
            await processUpdateModeDetail(result_topic7,StringSerialNumerInTableProjectSetup, host, port, username, password)
            print("result_topic7",result_topic7)
        elif topic in [topic8,topic9]:
            print("result_topic8",result_topic8)
            # If there is no timeout, there will be confusion between message man and message auto
            result_topic8 = message
            await pudSystempModeTrigerEachDeviceChange(result_topic8,StringSerialNumerInTableProjectSetup, host, port, username, password)
            # if user wirings
            # Đặt gBitManWrite = 1
            gBitManWrite = 1
            print("gBitManWrite before delay:", gBitManWrite)

            # Tạo một tác vụ để đặt lại gBitManWrite sau 10 giây
            asyncio.create_task(reset_gBitManWrite_after_delay(10))

            # In giá trị gBitManWrite ngay sau khi đặt
            print("gBitManWrite after setting:", gBitManWrite)

            print("result_topic8", result_topic8)
    except Exception as err:
        print(f"Error MQTT subscribe processMessage: '{err}'")  
        
async def reset_gBitManWrite_after_delay(delay):
    await asyncio.sleep(delay)
    global gBitManWrite
    gBitManWrite = 0
    print(f'gBitManWrite after reset: {gBitManWrite}')
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
async def processHandleMessagesDriver(client,StringSerialNumerInTableProjectSetup, host, port, username, password):
    
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = gzip_decompress(message.message)
            await processMessage(topic, payload, StringSerialNumerInTableProjectSetup, host, port, username, password)
    except Exception as err:
        print(f"Error processHandleMessagesDriver: '{err}'")
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processSudAllMessageFromMQTT(host, port, username, password, StringSerialNumerInTableProjectSetup, topic1, topic2, topic3, topic4, topic5, topic6,topic7,topic8,topic9,topic10):
    arrayTopic = [StringSerialNumerInTableProjectSetup + topic1, StringSerialNumerInTableProjectSetup + topic2, StringSerialNumerInTableProjectSetup +topic3, StringSerialNumerInTableProjectSetup +topic4, StringSerialNumerInTableProjectSetup +topic5, StringSerialNumerInTableProjectSetup +topic6, StringSerialNumerInTableProjectSetup +topic7, StringSerialNumerInTableProjectSetup +topic8, StringSerialNumerInTableProjectSetup +topic9, StringSerialNumerInTableProjectSetup +topic10]
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
            await processHandleMessagesDriver(client, StringSerialNumerInTableProjectSetup,host, port, username, password)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT processSudAllMessageFromMQTT: '{err}'")

async def main():
    StringSerialNumerInTableProjectSetup = ""
    tasks = []
    await initializeValueControlAuto()
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    if results_project != None :
        StringSerialNumerInTableProjectSetup=results_project[0]["serial_number"]
        #-------------------------------------------------------
        scheduler = AsyncIOScheduler()
        scheduler.add_job(confirmSystemModeAfterDeviceChangeOrUserChangeModeSystemp, 'cron',  second = f'*/1' , args=[StringSerialNumerInTableProjectSetup,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(getCpuInformation, 'cron',  second = f'*/1' , args=[StringSerialNumerInTableProjectSetup,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(selectAutoModeDetail, 'cron',  second = f'*/5' , args=[StringSerialNumerInTableProjectSetup,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(getValueProductionAndConsumtion, 'cron',  second = f'*/2' , args=[])
        scheduler.add_job(pudValueProductionAndConsumtionInMQTT, 'cron',  second = f'*/1' , args=[StringSerialNumerInTableProjectSetup,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.start()
        #-------------------------------------------------------
        tasks = []
        tasks.append(asyncio.create_task(processSudAllMessageFromMQTT(
                                                MQTT_BROKER,
                                                MQTT_PORT,
                                                MQTT_USERNAME,
                                                MQTT_PASSWORD,
                                                StringSerialNumerInTableProjectSetup,
                                                MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
                                                MQTT_TOPIC_SUD_MODEGET_INFORMATION,
                                                MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
                                                MQTT_TOPIC_SUD_DEVICES_ALL,
                                                MQTT_TOPIC_SUD_MODEGET_CPU,
                                                MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE,
                                                MQTT_TOPIC_SUD_CHOICES_MODE_AUTO_DETAIL,
                                                MQTT_TOPIC_SUD_CONTROL_MAN ,
                                                MQTT_TOPIC_SUD_MODIFY_DEVICE,
                                                MQTT_TOPIC_SUD_FEEDBACK_WRITE,
                                                )))
        # Move the gather outside the loop to wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())