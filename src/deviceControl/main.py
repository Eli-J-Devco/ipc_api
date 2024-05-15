# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import logging
import os
import sys
import mqttools
import asyncio
import json
import psutil
import platform
from datetime import datetime
import datetime


from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *

arr = sys.argv
ModeSysTemp = ""
flag = 0 
sent_information = ""
devices = []

enable_zero_export = 0
value_zero_export = 0
enable_power_limit = 0
value_power_limit = 0
percent_offset_power_limit = 0 
percent_offset_zero_export = 0 

value_production = 0
value_consumption = 0
value_cumulative = 0
value_subcumulative = 0
value_production_1h = 0
value_consumption_1h = 0
value_production_daily = 0
value_consumption_daily = 0
start_time_hourly = time.time()
start_time_daily = time.time()

total_power = 0
p_for_each_device_zero_export = 0
p_for_each_device_power_limit = 0

result_topic1 = []
result_topic4 = []
result_topic5 = []
bitcheck1 = 0

result_ModeSysTemp = []
result_ModeDevice = []
    
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
MQTT_TOPIC_PUD_PROJECT_SETUP = "/Project/Setup"
MQTT_TOPIC_PUD_CPU_SETUP = "/CPU/Information"
MQTT_TOPIC_SUD_MODEGET_INFORMATION = "/Project/Get"
MQTT_TOPIC_SUD_MODEGET_CPU = "/CPU/Get"
MQTT_TOPIC_SUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto"
MQTT_TOPIC_PUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto/Feedback"
MQTT_TOPIC_SUD_DEVICES_ALL = "/Devices/All"
MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT = "/Control/Write"
MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE = "/Project/Set"
MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE = "/Project/Set/Feedback"
MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS = "/Control/Process"
MQTT_TOPIC_PUD_MONIT_METER = "/Meter/Monitor"

def path_directory_relative(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from utils.logger_manager import LoggerSetup
arr = sys.argv
# setup root logger
# logger_setup = LoggerSetup(path,"ControlDevice")
# LOGGER = logging.getLogger(__name__)
"""
project_setup ->    mode_control 0=Man 1=Zero Export 2= Limit P,Q
Mode = Man -> value direct to function read device
Mode = Zero Export ->   
Mode = Limit -> 
"""
# Describe get_size cpu 
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def get_readable_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} YB"
# Describe convert_bytes_to_readable  
# 	 * @description get size
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {bytes,suffix}
# 	 * @return (size)
# 	 */  
def convert_bytes_to_readable(bytes_value, unit="KB"):
    if unit == "KB":
        return f"{bytes_value / 1024:.2f} KB"
    elif unit == "MB":
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    elif unit == "GB":
        return f"{bytes_value / (1024 ** 3):.2f} GB"
    else:
        return f"{bytes_value} B"
# Describe get_cpu_information 
# 	 * @description get cpu information
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
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
async def get_cpu_information(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global MQTT_TOPIC_PUD_CPU_SETUP
    topicPublic = serial_number_project + MQTT_TOPIC_PUD_CPU_SETUP
    timestamp = get_utc()
    try:
# Format system_info
        system_info = {
            "Timestamp": timestamp,
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
        system_info["MemoryInformation"]["Total"] = get_readable_size(svmem.total)
        system_info["MemoryInformation"]["Available"] = get_readable_size(svmem.available)
        system_info["MemoryInformation"]["Used"] = get_readable_size(svmem.used)
        system_info["MemoryInformation"]["Percentage"] = f"{svmem.percent}%"
        swap = psutil.swap_memory()
        system_info["MemoryInformation"]["SWAP"] = {
            "Total": get_readable_size(swap.total),
            "Free": get_readable_size(swap.free),
            "Used": get_readable_size(swap.used),
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
                    "TotalSize": get_readable_size(partition_usage.total),
                    "Used": get_readable_size(partition_usage.used),
                    "Free": get_readable_size(partition_usage.free),
                    "Percentage": f"{(partition_usage.used / partition_usage.total) * 100:.1f}%"
                }

                total_disk_size += partition_usage.total
                total_disk_used += partition_usage.used
            except PermissionError:
                continue

        total_disk_info = {
            "TotalSize": get_readable_size(total_disk_size),
            "Used": get_readable_size(total_disk_used),
            "Free": get_readable_size(total_disk_size - total_disk_used),
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

        system_info["NetworkSpeed"]["Upstream"] = convert_bytes_to_readable((net_io_counters.bytes_sent - net_io_counters_prev["TotalSent"]) / time_diff , unit="KB")
        system_info["NetworkSpeed"]["Downstream"] = convert_bytes_to_readable((net_io_counters.bytes_recv - net_io_counters_prev["TotalReceived"]) / time_diff , unit="KB")
        system_info["NetworkSpeed"]["TotalSent"] = get_readable_size(net_io_counters.bytes_sent)
        system_info["NetworkSpeed"]["TotalReceived"] = get_readable_size(net_io_counters.bytes_recv)
        system_info["NetworkSpeed"]["Timestamp"] = f"{current_time.hour}:{current_time.minute}:{current_time.second}"
        
        net_io_counters_prev["TotalSent"] = net_io_counters.bytes_sent
        net_io_counters_prev["TotalReceived"] = net_io_counters.bytes_recv
        net_io_counters_prev["Timestamp"] = current_time
# Disk I/O Information
        disk_io_counters = psutil.disk_io_counters()
        current_time = datetime.datetime.now()
        time_diff = (current_time - disk_io_counters_prev["Timestamp"]).total_seconds()

        system_info["DiskIO"]["SpeedRead"] = convert_bytes_to_readable((disk_io_counters.read_count - disk_io_counters_prev["ReadCount"]) / time_diff , unit="KB")
        system_info["DiskIO"]["SpeedWrite"] = convert_bytes_to_readable((disk_io_counters.write_count - disk_io_counters_prev["WriteCount"]) / time_diff , unit="KB")
        system_info["DiskIO"]["ReadBytes"] = get_readable_size(disk_io_counters.read_bytes)
        system_info["DiskIO"]["WriteBytes"] = get_readable_size(disk_io_counters.write_bytes)
        system_info["DiskIO"]["Timestamp"] = f"{current_time.hour}:{current_time.minute}:{current_time.second}"

        disk_io_counters_prev["ReadCount"] = disk_io_counters.read_count
        disk_io_counters_prev["WriteCount"] = disk_io_counters.write_count
        disk_io_counters_prev["Timestamp"] = current_time
# Push system_info to MQTT 
        push_data_to_mqtt(mqtt_host,
                            mqtt_port,
                            topicPublic,
                            mqtt_username,
                            mqtt_password,
                            system_info)
    except Exception as err:
        print(f"Error MQTT subscribe get_cpu_information: '{err}'")

# Describe pud_confirm_mode_control 
# 	 * @description pud_confirm_mode_control
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return ModeSysTemp
# 	 */ 
async def pud_confirm_mode_control(serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    global ModeSysTemp, flag, result_ModeSysTemp, result_ModeDevice
    result = []
    topic = serial_number_project + topicPublic
# Get ModeSysTemp from database when start program
    if result_ModeSysTemp is not None and result_ModeDevice is not None:
        if not ModeSysTemp and flag == 0:
            result = await MySQL_Select_v1("SELECT `project_setup`.`mode` FROM `project_setup`")
            ModeSysTemp = result[0]['mode']
# Have ModeSysTemp push to mqtt 
        if ModeSysTemp in (0, 1, 2):
            try:
                current_time = get_utc()
                data_send = {
                    "status": 200,
                    "confirm_mode": ModeSysTemp,
                    "time_stamp": current_time,
                }
                push_data_to_mqtt(mqtt_host, mqtt_port, topic, mqtt_username, mqtt_password, data_send)
                ModeSysTemp = None
                flag = 1
            except Exception as err:
                print(f"Error MQTT subscribe pud_confirm_mode_control: '{err}'")
# Describe process_update_mode_for_device_for_systemp 
# 	 * @description process_update_mode_for_device_for_systemp
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {result_topic1,bitcheck1,ModeSysTemp}
# 	 * @return ModeSysTemp
# 	 */ 
async def process_update_mode_for_device_for_systemp(serial_number_project, host, port, username, password):
# Global variables
    global result_topic1, bitcheck1, ModeSysTemp, flag, MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL, result_ModeSysTemp, result_ModeDevice
# Local variables
    topic = serial_number_project + MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL
    try:
        if result_topic1 and bitcheck1 == 1 :
            try:
                if result_topic1.get('id_device') == 'Systemp':
                    bitcheck1 = 0
                    ModeSysTemp = result_topic1.get('mode')  

                    querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
                    querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';;"

                    if ModeSysTemp in [0, 1, 2]:
                        result_ModeSysTemp = MySQL_Insert_v5(querysystemp, (ModeSysTemp,))
                    else :
                        print("Failed to insert data")
                    if ModeSysTemp in [0, 1]:
                        result_ModeDevice = MySQL_Insert_v5(querydevice, (ModeSysTemp,))
                    else:
                        pass
                    
                    if result_ModeSysTemp is None or result_ModeDevice is None:
                        current_time = get_utc()
                        data_send = {
                                "status" : 400,
                                "time_stamp" :current_time,
                                }
                        push_data_to_mqtt(host,
                                port,
                                topic ,
                                username,
                                password,
                                data_send)
                    else:
                        pass
            except Exception as json_err:
                print(f"Error processing JSON data: {json_err}")
        else:
            pass
            
    except Exception as err:
        print(f"Error MQTT subscribe process_update_mode_for_device_for_systemp: '{err}'")
# Describe pud_feedback_project_setup 
# 	 * @description pud_feedback_project_setup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return data_send
# 	 */ 
async def pud_feedback_project_setup(mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    query = "SELECT * FROM `project_setup`"
# Get information from database
    result = await MySQL_Select_v1(query)
    if result:
        try:
# Sent information to Mqtt
            data_send = result[0]
            data_send['mqtt'] = [
                {"time_stamp": get_utc()},
                {"status": 200}
            ]
            push_data_to_mqtt(mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password, data_send)
        except Exception as err:
            print(f"Error MQTT subscribe pud_feedback_project_setup: '{err}'")
    else:
        pass
# Describe insert_information_project_setup 
# 	 * @description insert_information_project_setup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return data_send
# 	 */ 
async def insert_information_project_setup(mqtt_result, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    topic = topicPublic
    try:
# separate mqtt information on sent infromation
        result_set = mqtt_result.get('parameter', {})
        result_set.pop('mqtt', None)
# Filter the received results to create a query to update database information
        if result_set:
            update_fields = ", ".join([f"{field} = %s" for field, value in result_set.items()])
            update_values = [value for field, value in result_set.items()]
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
                push_data_to_mqtt(mqtt_host, mqtt_port, topic, mqtt_username, mqtt_password, data_send)
        else:
            current_time = get_utc()
            data_send = {
                "status": 200,
                "time_stamp": current_time
            }
            push_data_to_mqtt(mqtt_host, mqtt_port, topic, mqtt_username, mqtt_password, data_send)
    except Exception as err:
        print(f"Error MQTT subscribe insert_information_project_setup: '{err}'")
# Describe pud_information_project_setup_when_request 
# 	 * @description pud_information_project_setup_when_request
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result ,serial_number_project,host, port, username, password}
# 	 * @return call pud_feedback_project_setup
# 	 */ 
async def pud_information_project_setup_when_request(mqtt_result ,serial_number_project,host, port, username, password):
    global MQTT_TOPIC_PUD_PROJECT_SETUP
    topicpud = serial_number_project + MQTT_TOPIC_PUD_PROJECT_SETUP
    current_time = get_utc()
    try:
        if mqtt_result and 'get_information' in mqtt_result:
            await pud_feedback_project_setup(host,
                                            port,
                                            topicpud,
                                            username,
                                            password)                       
        else:
            pass
    except Exception as err:
        data_send = {
            "mqtt": [
                    {"time_stamp" : current_time},
                    {"status":400}]
                    }
        push_data_to_mqtt(host, port, topicpud, username, password, data_send)
# Describe insert_information_project_setup_when_request 
# 	 * @description insert_information_project_setup_when_request
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result ,serial_number_project,host, port, username, password}
# 	 * @return call insert_information_project_setup
# 	 */ 
async def insert_information_project_setup_when_request(mqtt_result ,serial_number_project,host, port, username, password):
    global MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE
    topicpud = serial_number_project + MQTT_TOPIC_PUD_SET_PROJECTSETUP_DATABASE
    try:
        if mqtt_result and 'set_information' in mqtt_result:
            await insert_information_project_setup(mqtt_result,
                                            host,
                                            port,
                                            topicpud,
                                            username,
                                            password)                       
        else:
            pass
    except Exception as err:
        print(f"Error MQTT subscribe insert_information_project_setup_when_request: '{err}'") 
# Describe check_inverter_device 
# 	 * @description check_inverter_device
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {device_control}
# 	 * @return devivce is inverter 
# 	 */ 
async def check_inverter_device(device_control):
    results_device_type = []
    
    query = "SELECT `device_type`.`name` FROM device_type INNER JOIN `device_list` ON device_list.id_device_type=device_type.id WHERE device_list.id=%s;"
    results_device_type = MySQL_Select(query, (device_control,))
    if results_device_type and results_device_type[0]["name"] == "PV System Inverter":
        return True  
    else:
        return False  
# Describe get_list_device_in_automode 
# 	 * @description get_list_device_in_automode
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
async def get_list_device_in_automode(mqtt_result):
    global total_power
    device_list = []

    if mqtt_result and isinstance(mqtt_result, list):
        for item in mqtt_result:
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                status_device = item['status_device']
# Check device On/Off
                value_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ControlINV"]
                if value_array:
                    value = value_array[0]
# Check device Fault
                operator_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
                if operator_array:
                    operator = operator_array[0]
# device is inv , online , auto , not fault => control 
                if await check_inverter_device(id_device) and status_device == 'online' and mode == 1 and operator not in [7, 8]:
# get information pmax , pmax customer , pmin
                    result_pmax_custom = MySQL_Select("SELECT rated_power_custom FROM `device_list` WHERE id = %s", (id_device,))
                    p_max_custom = result_pmax_custom[0]["rated_power_custom"]
                    result_pmax = MySQL_Select("SELECT rated_power FROM `device_list` WHERE id = %s", (id_device,))
                    p_max = result_pmax[0]["rated_power"]
                    result_pmin_percent = MySQL_Select("SELECT min_watt_in_percent FROM `device_list` WHERE id = %s", (id_device,))
                    p_min_percent = result_pmin_percent[0]["min_watt_in_percent"]
                    if p_max and p_min_percent:
                        p_min = (p_max*p_min_percent)/100
# create list sent mqtt 
                    device_list.append({
                        'id_device': id_device,
                        'mode': mode,
                        'status_device': status_device,
                        'p_max': p_max_custom,
                        'p_min': p_min,
                        'controlinv': value,
                        'operator': operator,
                    })
    total_power = sum(device['p_max'] for device in device_list)
    return device_list
# Describe get_list_device_in_process 
# 	 * @description get_list_device_in_process
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
async def get_list_device_in_process(mqtt_result, serial_number_project, host, port, username, password):
    global total_power, MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS

    device_list = []
    operator_array = []
    wmax_array = []
    realpower_array = []
    operator = 0
    operator_text = ""
    wmax = 0.0
    realpower = 0.0
    current_time = get_utc()

    if mqtt_result and isinstance(mqtt_result, list):
        for item in mqtt_result:
# get info about device
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                status_device = item['status_device']
                p_max_custom = item['rated_power_custom']
                p_min_percent = item['min_watt_in_percent']
                device_name = item['device_name']
# check device is inv
                if await check_inverter_device(id_device):
# get info list device
                    operator_text = {
                        0: "shutting down",
                        1: "shutting down",
                        4: "running",
                        5: "running",  
                        6: "shutting down",
                        7: "fault",
                    }
                    operator_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
                    operator = operator_array[0] if operator_array else 0
                    operator_text = operator_text.get(operator, "off")
                    
                    wmax_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "WMax"]
                    wmax = wmax_array[0] if wmax_array else 0
                    
                    realpower_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ACActivePower"]
                    realpower = realpower_array[0] if realpower_array else 0
# device offline   
                    if status_device == 'offline':
                        realpower = 0.0
                        operator_text = "off"
# Calculate pmin   
                    if p_max_custom and p_min_percent:
                        p_min = round((p_max_custom * p_min_percent) / 100, 4)
                    else:
                        p_min = 0.0
                    # create list sent mqtt
                    device_list.append({
                        'id_device': id_device,
                        'device_name': device_name,
                        'mode': mode,
                        'status_device': status_device,
                        'operator': operator_text,
                        'p_max': p_max_custom,
                        'p_min': p_min,
                        'wmax': wmax,
                        'realpower': realpower,
                        'timestamp': current_time,
                    })

    push_data_to_mqtt(host, port, serial_number_project + MQTT_TOPIC_PUD_LIST_DEVICE_PROCESS, username, password, device_list)
    return device_list
# Describe get_value_meter 
# 	 * @description get_value_meter
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return value_production ,value_consumption
# 	 */ 
async def get_value_meter():
# Global variables
    global result_topic4, value_production, value_consumption ,value_production_1h, value_consumption_1h,value_production_daily,value_consumption_daily, start_time_hourly , start_time_daily
# Local variables
    value_production_aray = []
    value_consumption_aray = []
    total_value_production = 0
    total_value_consumption = 0
    value_production_integral = 0
    value_consumption_integral = 0
    last_update_time = start_time_hourly
    current_time = time.time()
# Get Topic /Devices/All
    if result_topic4:
        for item in result_topic4:
            if 'id_device' in item:
                id_device = item['id_device']
# Select type Meter
                result_type_meter = MySQL_Select("SELECT `device_type`.`name` FROM `device_type` INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id WHERE `device_list`.id = %s", (id_device,))
# Caculator Value Meter Production
                if result_type_meter:
                    if result_type_meter[0]["name"] == "Production Meter":
                        value_production_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if len(value_production_aray) > 0 and value_production_aray[0] is not None:
                            total_value_production += value_production_aray[0]
                            value_production = total_value_production
                            current_time = time.time()
                            dt = current_time - last_update_time
                            value_production_integral += value_production * dt/3600
                            last_update_time = current_time
                            print("value_production_integral",value_production_integral)
# Caculator Value Meter Consumption
                    elif result_type_meter[0]["name"] == "Consumption meter":
                        value_consumption_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if len(value_consumption_aray) > 0 and value_consumption_aray[0] is not None:
                            total_value_consumption += value_consumption_aray[0]
                            value_consumption = total_value_consumption
                            current_time = time.time()
                            dt = current_time - last_update_time
                            value_consumption_integral += value_consumption * dt/3600
                            last_update_time = current_time
                            print("value_consumption_integral",value_consumption_integral)
# Check if 1 hour has passed and Reset variable
                    # current_hour = int(current_time // 3600)
                    # current_day = int(current_time // (3600 * 24))
                    current_hour = int(current_time // 60)
                    current_day = int(current_time // 1800)
                    # if current_hour != int(start_time_hourly // 3660):
                    if current_hour != int(start_time_hourly // 60):
                        value_production_1h = round(value_production_integral)
                        value_consumption_1h = round(value_consumption_integral)
                        value_production_daily += value_production_1h
                        value_consumption_daily += value_consumption_1h
                        value_production_integral = 0
                        value_consumption_integral = 0
                        start_time_hourly = current_time

                    # if current_day != int(start_time_daily // (3600 * 24)):
                    if current_day != int(start_time_daily // 1800):
                        value_production_daily = 0
                        value_consumption_daily = 0
                        start_time_daily = current_time
                else:
                    pass
    else:
        pass    
async def monit_value_meter(serial_number_project,mqtt_host,mqtt_port,mqtt_username,mqtt_password):
    global result_topic4 ,value_production, value_consumption ,value_production_1h, value_consumption_1h,value_production_daily,value_consumption_daily,MQTT_TOPIC_PUD_MONIT_METER
    timestamp = get_utc()
    topicPublic = serial_number_project + MQTT_TOPIC_PUD_MONIT_METER
    max_production = 0.0
# Format data
    try:
        value_metter = {
        "Timestamp": timestamp,
        "instant": {},
        "hourly": {},
        "daily": {},
        }
        
        if result_topic4:
            for device in result_topic4:
                if "mppt" in device:
                    for mppt in device["mppt"]:
                        if "power" in mppt:
                            max_production += mppt["power"]
# instant power
        value_metter["instant"]["production"] = round(value_production / 1000, 4)
        value_metter["instant"]["consumption"] = round(value_consumption / 1000, 4)
        value_metter["instant"]["grid_feed"] = round((value_production - value_consumption) / 1000, 4)
        value_metter["instant"]["max_production"] = round(max_production / 1000, 4)
# hourly power
        value_metter["hourly"]["production"] = round(value_production_1h / 1000, 4)
        value_metter["hourly"]["consumption"] = round(value_consumption_1h / 1000, 4)
        value_metter["hourly"]["grid_feed"] = round((value_production_1h - value_consumption_1h) / 1000, 4)
# daily power
        value_metter["daily"]["production"] = round(value_production_daily / 1000, 4)
        value_metter["daily"]["consumption"] = round(value_consumption_daily / 1000, 4)
        value_metter["daily"]["grid_feed"] = round((value_production_daily - value_consumption_daily) / 1000, 4)
# Push system_info to MQTT 
        push_data_to_mqtt(mqtt_host,
                            mqtt_port,
                            topicPublic,
                            mqtt_username,
                            mqtt_password,
                            value_metter)
    except Exception as err:
        print(f"Error MQTT subscribe get_cpu_information: '{err}'")
# Describe process_caculator_p_power_limit 
# 	 * @description process_caculator_p_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return p_for_each_device_power_limit
# 	 */ 
async def process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4, enable_power_limit, enable_zero_export, value_power_limit, devices, value_cumulative, value_subcumulative, value_production, total_power, MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT, p_for_each_device_power_limit 
# Check device equipment qualified for control
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)
# get information about power in database and varaable devices
    if devices:
        device_list_control_power_limit = []
        for device in devices:
            power_max = device["p_max"]
            id_device = device["id_device"]
            if id_device :
                result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`name` = 'Power Limit' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s ", (id_device,))
                slope = float(result_slope[0]["slope"])
# Convert power real 
            if power_max and slope:
                delta = slope * 1000
                power_max_convert = (power_max / slope) * delta
                p_max_real = (total_power / slope) * delta
                efficiency_total = (value_power_limit/p_max_real)
                if efficiency_total > 1 :
                        efficiency_total = 1
                p_for_each_device_power_limit = (efficiency_total * power_max_convert) / delta
                if p_for_each_device_power_limit > power_max_convert/delta:
                    p_for_each_device_power_limit = (power_max_convert/delta)
# Check device is off , on device 
            if device['controlinv'] == 1:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "power limit",
                    "setpoint": value_power_limit,
                    "parameter": [
                        {"id_pointkey": "WMax", "value": p_for_each_device_power_limit}
                    ]
                }
            elif device['controlinv'] == 0:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "power limit",
                    "setpoint": value_power_limit,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": p_for_each_device_power_limit}
                    ]
                }
# Accumulate devices that are eligible to run automatically to push to mqtt
            device_list_control_power_limit.append(new_device)
        if len(devices) == len(device_list_control_power_limit) and enable_zero_export == 0:
            push_data_to_mqtt(mqtt_host, mqtt_port, serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT, mqtt_username, mqtt_password, device_list_control_power_limit)
            print("Value setpoint", value_power_limit)
            print("P Feedback production", value_production)
            print("P Feedback consumption", value_consumption)
            p_for_each_device_power_limit = 0

# Describe process_caculator_zero_export 
# 	 * @description process_caculator_zero_export
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return p_for_each_device_zero_export
# 	 */ 
async def process_caculator_zero_export(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
# Global variables
    global result_topic4 ,enable_power_limit , value_zero_export , value_consumption , devices , value_cumulative ,value_subcumulative , value_production ,total_power ,MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT,p_for_each_device_zero_export
# Local variables
    efficiency_total = 0
    power_max = 0
    id_device = 0
    result_slope = []
    slope = 1.0
    power_max_convert = 0
    p_max_real = 0
    delta = 1
    total_p_inv_prodution = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
# The actual setting value is equal to the consumption meter value minus the user-set error value
    if value_consumption > 0 :
        value_consumption = value_consumption - (value_consumption*value_zero_export/100)
    else:
        value_consumption = 0
# Check device equipment qualified for control
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)
# get information about power in database and varaable devices
    if devices : 
        device_list_control_power_limit = []
        for device in devices:
            power_max = device["p_max"]
            id_device = device["id_device"]
            if id_device :
                result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`name` = 'Power Limit' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s ", (id_device,))
                if result_slope :
                    slope = float(result_slope[0]["slope"])
                else:
                    pass
# Convert power real 
            if power_max and slope:
                if total_power and value_consumption :  
                    delta = slope*1000
                    power_max_convert = ((power_max/slope)*delta)
                    p_max_real = ((total_power/slope)*delta)
# Calculate the total performance of the system
                    efficiency_total = (value_consumption/p_max_real)
                    if efficiency_total > 1 :
                        efficiency_total = 1
                    else:
                        pass
# Calculate the performance for each device based on the total performance
                if efficiency_total:
                    p_for_each_device_zero_export = ((efficiency_total*power_max_convert)/delta)
                if p_for_each_device_zero_export > power_max_convert/delta:
                    p_for_each_device_zero_export = (power_max_convert/delta)
                else:
                    pass
            if p_for_each_device_zero_export <= 0 :
                p_for_each_device_zero_export = 0 
            else:
                pass# Check device is off , on device 
            total_p_inv_prodution += p_for_each_device_zero_export
            if device['controlinv'] == 1:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export",
                    "setpoint": value_consumption,
                    "parameter": [
                        {"id_pointkey": "WMax", "value": p_for_each_device_zero_export}
                    ]
                }
            elif device['controlinv'] == 0:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export",
                    "setpoint": value_consumption,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": p_for_each_device_zero_export}
                    ]
                }
            else:
                pass
            device_list_control_power_limit.append(new_device)
# check the consumption is too small with the total output output 0 to the control
        if value_consumption < total_p_inv_prodution :
            new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export",
                    "setpoint": value_consumption,
                    "parameter": [
                        {"id_pointkey": "WMax", "value": 0}
                    ]
                }
            push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
        else:
            pass
# Push data to mqtt 
        if len(devices) == len(device_list_control_power_limit) and enable_power_limit == 0 :
            push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            print("Value setpoint",value_consumption)
            print("P Feedback production",value_production)
            print("P Feedback consumption",value_consumption)
            p_for_each_device_zero_export = 0
        else:
            pass
    else:
        pass
# Describe process_caculator_zero_export_power_limit 
# 	 * @description process_caculator_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return p_for_each_device
# 	 */ 
async def process_caculator_zero_export_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
# Global variables
    global result_topic4,enable_power_limit,value_zero_export,value_consumption,devices,value_cumulative,value_subcumulative,value_production,total_power,MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT,p_for_each_device_zero_export,p_for_each_device_power_limit
# Local variables
    p_for_each_device = 0
    power_max_convert = 0
    delta = 1
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
# Get value control INV 
    await process_caculator_zero_export(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
    await process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
# get information about power in database and varable devices
    if devices : 
        device_list_control_power_limit = []
        for device in devices:
            power_max = device["p_max"]
            id_device = device["id_device"]
# Convert power max real 
            if id_device :
                result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`name` = 'Power Limit' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s ", (id_device,))
                slope = float(result_slope[0]["slope"])
            if power_max and slope:
                if total_power and value_consumption :  
                    # difference coefficient between actual and value in inv 333 with 3330 = 0.1
                    delta = slope*1000
                    power_max_convert = round((power_max/slope)*delta)
# Power for each device 
            await process_caculator_zero_export(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
            await process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
            if p_for_each_device_zero_export and p_for_each_device_power_limit :
                p_for_each_device = round (p_for_each_device_zero_export + p_for_each_device_power_limit)
            # if p_for_each_device > power_max_convert/delta:
            #         p_for_each_device = power_max_convert/delta
            # else:
            #     pass
# Check device is off , on device 
            print("P Feedback production",value_production)
            print("P Feedback consumption",value_consumption)
            print("p_for_each_device",p_for_each_device)
            print("power_max_convert",power_max_convert)
            print("delta",delta)
            print("p_for_each_device_zero_export",p_for_each_device_zero_export)
            print("p_for_each_device_power_limit",p_for_each_device_power_limit)
            print("slope",slope)
            print("devices",devices)
            
            if device['controlinv'] == 1:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export + power limit",
                    "setpoint": value_consumption + value_power_limit,
                    "parameter": [
                        {"id_pointkey": "WMax", "value": p_for_each_device}
                    ]
                }
            else:
                new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export + power limit",
                    "setpoint": value_consumption + value_power_limit,
                    "parameter": [
                        {"id_pointkey": "ControlINV", "value": 1},
                        {"id_pointkey": "WMax", "value": p_for_each_device}
                    ]
                }
            device_list_control_power_limit.append(new_device)
# Push data to mqtt 
        if len(devices) == len(device_list_control_power_limit) :
            push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
        else:
            pass
    else:
        pass
# Describe process_not_choose_zero_export_power_limit 
# 	 * @description process_not_choose_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return power_max
# 	 */ 
async def process_not_choose_zero_export_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
# Global variables
    global result_topic4 , devices ,MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
# Local variables
    power_max = 0
    result_slope = []
    slope = 1.0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    p_for_each_device = 0
# Check device equipment qualified for control
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)
# get information about power in database and varable devices
    if devices :
            device_list_control_power_limit = []
            for device in devices:
                id_device = device["id_device"]
                power_max = device["p_max"]
                power_max = float(power_max)
# Convert power max real 
                if id_device :
                    result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`name` = 'Power Limit' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s ", (id_device,))
                    slope = float(result_slope[0]["slope"])
                if power_max and slope :
                    p_for_each_device = power_max/slope
# Check device is off , on device 
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "status": "full Power",
                        "parameter": [
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "status": "full Power",
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                device_list_control_power_limit.append(new_device)
# Push data to mqtt 
            if len(devices) == len(device_list_control_power_limit):
                push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
                print("P Feedback production",value_production)
                print("P Feedback consumption",value_consumption)
                print("Value INV Out",p_for_each_device)
            else:
                pass
    else:
        pass 
# Describe process_update_zeroexport_powerlimit 
# 	 * @description process_update_zeroexport_powerlimit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result,serial_number_project, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password}
# 	 * @return MySQL_Update enable_zero_export ,value_zero_export,enable_power_limit,value_power_limit
# 	 */ 
async def process_update_zeroexport_powerlimit(mqtt_result,serial_number_project, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password ):
# Global variables
    global enable_zero_export,value_zero_export,enable_power_limit,value_power_limit,percent_offset_power_limit,percent_offset_zero_export,MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
# Local variables
    bitchecktopic3 = 0
    topicPudModeAuto = serial_number_project + MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
    current_time = get_utc()
    mode_auto = ""
    type_mode_auto = ""
    comment = 0
    result_checkbox_zero_export = []
    result_textbox_zero_export = []
    result_checkbox_power_limit = []
    result_textbox_power_limit = []
# Receve data from mqtt
    try:
        if mqtt_result and 'mode' in mqtt_result and 'type' in mqtt_result and 'enable' in mqtt_result and 'value' in mqtt_result:
            mode_auto = mqtt_result['mode'] 
            type_mode_auto = mqtt_result['type']
            bitchecktopic3 = 1
# Compare get information update database 
            if mode_auto == "zero_export":
                if type_mode_auto == "checkbox":
                    enable_zero_export = mqtt_result.get('enable', enable_zero_export)
                    if enable_zero_export is not None:
                        result_checkbox_zero_export = MySQL_Update_V1("update project_setup set enable_zero_export = %s", (enable_zero_export,))
                        print("result_checkbox_zero_export",result_checkbox_zero_export)
                elif type_mode_auto == "textbox":
                    value_zero_export = mqtt_result.get('value', value_zero_export)
                    if 0 <= value_zero_export <= 100:
                        result_textbox_zero_export = MySQL_Update_V1("update project_setup set value_zero_export = %s", (value_zero_export,))
                        print("result_textbox_zero_export",result_textbox_zero_export)
            elif mode_auto == "power_limit":
                if type_mode_auto == "checkbox":
                    enable_power_limit = mqtt_result.get('enable', enable_power_limit)
                    if enable_power_limit is not None:
                        result_checkbox_power_limit = MySQL_Update_V1("update project_setup set enable_power_limit = %s", (enable_power_limit,))
                        print("result_checkbox_power_limit",result_checkbox_power_limit)
                elif type_mode_auto == "textbox":
                    value_power_limit = mqtt_result.get('value', value_power_limit)
                    if value_power_limit is not None:
                        result_textbox_power_limit = MySQL_Update_V1("update project_setup set value_power_limit = %s", (value_power_limit,))
                        print("result_textbox_power_limit",result_textbox_power_limit)
                        percent_offset_power_limit = mqtt_result.get('offset', percent_offset_power_limit)
                        value_power_limit = (value_power_limit + (value_power_limit*percent_offset_power_limit)/100)*1000
                        print("value_power_limit",value_power_limit)
                if 0 <= percent_offset_power_limit <= 100:
                    MySQL_Update_V1("update project_setup set value_offset_power_limit = %s", (percent_offset_power_limit,))
                else:
                    pass
# When you receive one of the above information, give feedback to mqtt
            if ( enable_zero_export or value_zero_export or enable_power_limit or value_power_limit ) and bitchecktopic3 == 1 :
                if result_checkbox_zero_export == None or result_textbox_zero_export == None or result_textbox_power_limit == None or result_checkbox_power_limit == None :
                    comment = 400 
                else:
                    comment = 200 
                data_send = {
                            "time_stamp" :current_time,
                            "status":comment, 
                            }
                push_data_to_mqtt(mqtt_host,
                        mqtt_port,
                        topicPudModeAuto ,
                        mqtt_username,
                        mqtt_password,
                        data_send)
                bitchecktopic3 = 0
            else:
                pass
            
    except Exception as err:
        print(f"Error MQTT subscribe process_update_zeroexport_powerlimit: '{err}'")
# Describe process_getfirst_zeroexport_powerlimit 
# 	 * @description process_getfirst_zeroexport_powerlimit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return enable_zero_export ,value_zero_export,enable_power_limit,value_power_limit
# 	 */ 
async def process_getfirst_zeroexport_powerlimit():
# Global variables
    global enable_zero_export,value_zero_export,enable_power_limit,value_power_limit,percent_offset_power_limit
# Local variables
    value_power_limit_temp = 0
    result_project_setup = []
# Get database information the first time
    try:
        result_project_setup = await MySQL_Select_v1("select * from project_setup")
        if result_project_setup :
            enable_zero_export = result_project_setup[0]["enable_zero_export"]
            value_zero_export = result_project_setup[0]["value_zero_export"]
            enable_power_limit = result_project_setup[0]["enable_power_limit"]
            value_power_limit_temp = result_project_setup[0]["value_power_limit"]
            percent_offset_power_limit = result_project_setup[0]["value_offset_power_limit"]
            value_power_limit = (value_power_limit_temp + (value_power_limit_temp*percent_offset_power_limit)/100)*1000
        else:
            pass
            
    except Exception as err:
        print(f"Error MQTT subscribe process_getfirst_zeroexport_powerlimit: '{err}'")   
# Describe process_zero_export_power_limit 
# 	 * @description process_zero_export_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return chosse process zero_export ,power_limit ,zero_export + power_limit , Auto - Full P
# 	 */ 
async def process_zero_export_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password):
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
# Select the auto run process
    if enable_zero_export == 1 and enable_power_limit == 0:
        print("==============================zero_export==============================")
        await process_caculator_zero_export(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    elif enable_power_limit == 1 and value_power_limit != 0 and enable_zero_export == 0:
        print("==============================power_limit==============================")
        await process_caculator_p_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    elif enable_zero_export == 1 and enable_power_limit == 1 :
        print("=======================zero_export + power_limit========================")
        await process_caculator_zero_export_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    else :
        print("======================= Auto - Full P ========================")
        await process_not_choose_zero_export_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
# Describe process_message 
# 	 * @description processmessage from mqtt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,serial_number_project, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def process_message(topic, message,serial_number_project, host, port, username, password):

    global MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    global MQTT_TOPIC_SUD_MODEGET_INFORMATION
    global MQTT_TOPIC_SUD_CHOICES_MODE_AUTO
    global MQTT_TOPIC_SUD_DEVICES_ALL
    global MQTT_TOPIC_SUD_MODEGET_CPU
    global MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE
                                                    
    result_topic2 = ""
    result_topic3 = ""
    result_topic5 = ""
    result_topic6 = ""
    global result_topic4
    global result_topic1
    global bitcheck1 

    topic1 = serial_number_project + MQTT_TOPIC_SUD_MODECONTROL_DEVICE
    topic2 = serial_number_project + MQTT_TOPIC_SUD_MODEGET_INFORMATION
    topic3 = serial_number_project + MQTT_TOPIC_SUD_CHOICES_MODE_AUTO
    topic4 = serial_number_project + MQTT_TOPIC_SUD_DEVICES_ALL
    topic5 = serial_number_project + MQTT_TOPIC_SUD_MODEGET_CPU
    topic6 = serial_number_project + MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE
    
    try:
        if topic == topic1:
            result_topic1 = message
            bitcheck1 = 1
            await process_update_mode_for_device_for_systemp (serial_number_project, host, port, username, password)
            print("result_topic1",result_topic1)
        elif topic == topic2:
            result_topic2 = message
            await pud_information_project_setup_when_request(result_topic2,serial_number_project, host, port, username, password)
            print("result_topic2",result_topic2)
        elif topic == topic3:
            result_topic3 = message
            await process_update_zeroexport_powerlimit(result_topic3,serial_number_project,host, port, username, password)
            print("result_topic3",result_topic3)
        elif topic == topic4:
            result_topic4 = message
            await get_list_device_in_process(result_topic4,serial_number_project, host, port, username, password)
        elif topic == topic5:
            result_topic5 = message
        elif topic == topic6:
            result_topic6 = message
            await insert_information_project_setup_when_request(result_topic6,serial_number_project, host, port, username, password)
            print("result_topic6",result_topic6)
    except Exception as err:
        print(f"Error MQTT subscribe process_message: '{err}'")
# Describe sub_mqtt 
# 	 * @description sub_mqtt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def sub_mqtt(serial_number_project, host, port, topic1, topic2, topic3, topic4, topic5, topic6, username, password):
    topics = [topic1, topic2, topic3, topic4, topic5, topic6]
    
    while True:
        try:
            client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
            if not client:
                return -1
            
            await client.start()
            for topic in topics:
                await client.subscribe(serial_number_project + topic)

            while True:
                message = await asyncio.wait_for(client.messages.get(), timeout=5.0)
                if message:
                    payload = json.loads(message.message.decode())
                    topic = message.topic
                    await process_message(topic, payload, serial_number_project, host, port, username, password)
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"Error while processing message: {e}")
            print('Connection lost. Trying to reconnect...')
            await client.stop()
            await asyncio.sleep(5)  # Wait for 5 seconds before trying to reconnect

async def main():
    serial_number_project = ""
    tasks = []
    await process_getfirst_zeroexport_powerlimit()
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    if results_project != None :
        serial_number_project=results_project[0]["serial_number"]
        #-------------------------------------------------------
        scheduler = AsyncIOScheduler()
        scheduler.add_job(pud_confirm_mode_control, 'cron',  second = f'*/1' , args=[serial_number_project,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(get_cpu_information, 'cron',  second = f'*/1' , args=[serial_number_project,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(process_zero_export_power_limit, 'cron',  second = f'*/5' , args=[serial_number_project,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(get_value_meter, 'cron',  second = f'*/1' , args=[])
        scheduler.add_job(monit_value_meter, 'cron',  second = f'*/1' , args=[serial_number_project,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.start()
        #-------------------------------------------------------
        tasks = []
        tasks.append(asyncio.create_task(sub_mqtt(serial_number_project,
                                                        MQTT_BROKER,
                                                        MQTT_PORT,
                                                        MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
                                                        MQTT_TOPIC_SUD_MODEGET_INFORMATION,
                                                        MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
                                                        MQTT_TOPIC_SUD_DEVICES_ALL,
                                                        MQTT_TOPIC_SUD_MODEGET_CPU,
                                                        MQTT_TOPIC_SUD_SET_PROJECTSETUP_DATABASE,
                                                        MQTT_USERNAME,
                                                        MQTT_PASSWORD
                                                        )))
        # Move the gather outside the loop to wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        pass
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())