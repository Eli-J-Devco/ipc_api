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

total_power = 0
p_for_each_device_zero_export = 0
p_for_each_device_power_limit = 0

result_topic1 = []
result_topic4 = []
result_topic5 = []
bitcheck1 = 0

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
def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
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
        system_info = {
            "Timestamp": timestamp,
            "SystemInformation": {},
            "BootTime": {},
            "CPUInfo": {},
            "MemoryInformation": {},
            "DiskInformation": {},
            "NetworkInformation": {}
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
        system_info["MemoryInformation"]["Total"] = get_size(svmem.total)
        system_info["MemoryInformation"]["Available"] = get_size(svmem.available)
        system_info["MemoryInformation"]["Used"] = get_size(svmem.used)
        system_info["MemoryInformation"]["Percentage"] = f"{svmem.percent}%"
        swap = psutil.swap_memory()
        system_info["MemoryInformation"]["SWAP"] = {
            "Total": get_size(swap.total),
            "Free": get_size(swap.free),
            "Used": get_size(swap.used),
            "Percentage": f"{swap.percent}%"
        }

        # Disk Information
        total_disk_size = 0
        total_disk_used = 0
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                total_disk_size += partition_usage.total
                total_disk_used += partition_usage.used
            except PermissionError:
                continue
        
        system_info["DiskInformation"] = {
            "TotalSize": get_size(total_disk_size),
            "Used": get_size(total_disk_used),
            "Free": get_size(total_disk_size - total_disk_used),
            "Percentage": f"{(total_disk_used / total_disk_size) * 100:.1f}%"
        }

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
        
        push_data_to_mqtt(mqtt_host,
                            mqtt_port,
                            topicPublic,
                            mqtt_username,
                            mqtt_password,
                            system_info)
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
# Describe pud_confirm_mode_control 
# 	 * @description pud_confirm_mode_control
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return ModeSysTemp
# 	 */ 
async def pud_confirm_mode_control(serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    print("da vao day pud_confirm_mode_control")
    global ModeSysTemp
    global flag 
    result = []
    topic = serial_number_project + topicPublic 
    if not ModeSysTemp and flag == 0:
        query = "SELECT `project_setup`.`mode` FROM `project_setup`"
        result = await MySQL_Select_v1(query) 
        ModeSysTemp = result[0]['mode']
        
        print("ModeSysTemp",ModeSysTemp)
        
    if ModeSysTemp == 0 or ModeSysTemp == 1 or ModeSysTemp == 2:
        try:
            current_time = get_utc()
            data_send = {
                    "status" : 200,
                    "confirm_mode":ModeSysTemp,
                    "time_stamp" :current_time,
                    }
            push_data_to_mqtt(mqtt_host,
                    mqtt_port,
                    topic ,
                    mqtt_username,
                    mqtt_password,
                    data_send)
            ModeSysTemp = None
            flag = 1 
        except Exception as err:
            print(f"Error MQTT subscribe: '{err}'")
    else :
        pass
# Describe process_update_mode_for_device_for_systemp 
# 	 * @description process_update_mode_for_device_for_systemp
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {result_topic1,bitcheck1,ModeSysTemp}
# 	 * @return ModeSysTemp
# 	 */ 
async def process_update_mode_for_device_for_systemp(serial_number_project, host, port, username, password):
    print("da vao day process_update_mode_for_device_for_systemp")
    global result_topic1
    global bitcheck1
    global ModeSysTemp
    global MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL
    result_ModeSysTemp = []
    result_ModeDevice = []
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
                        print("da vao loi")
                        print("result_ModeSysTemp",result_ModeSysTemp)
                        print("result_ModeDevice",result_ModeDevice)
                        print("topic",topic)
                        current_time = get_utc()
                        data_send = {
                                "status" : 400,
                                "confirm_mode": ModeSysTemp,
                                "time_stamp" :current_time,
                                }
                        push_data_to_mqtt(host,
                                port,
                                topic ,
                                username,
                                password,
                                data_send)
                    else:
                        print("khong vao loi")
                        print("result_ModeSysTemp",result_ModeSysTemp)
                        print("result_ModeDevice",result_ModeDevice)
                        pass
            except Exception as json_err:
                print(f"Error processing JSON data: {json_err}")
        else:
            pass
            
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
# Describe pud_feedback_project_setup 
# 	 * @description pud_feedback_project_setup
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return data_send
# 	 */ 
async def pud_feedback_project_setup(mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    result = []
    topic = topicPublic 
    name = ""
    serial_number = ""
    location = ""
    description = ""
    administrative_contact = ""
    id_first_page_on_login = ""
    id_logging_interval = ""
    id_scheduled_upload_time = ""
    number_times_retry = ""
    id_time_wait_before_retry = ""
    id_upload_debug_information = ""
    enable_upload_data_on_alarm_status = ""
    enable_upload_data_on_low_disk = ""
    enable_upload_data_on_system_startup = ""
    link_remote_access = ""
    allow_remote_access = ""
    enable_static_routing = ""
    mode = ""
    id_time_zone = ""
    Time1cycle = ""
    sampling_time1cycle = ""
    enable_zero_export = ""
    value_zero_export = ""
    enable_power_limit = ""
    value_power_limit = ""
    value_offset_power_limit = ""
    powermeter_target_point = ""
    powermeter_tolerance = ""
    powermeter_max_point = ""
    slow_approx_limit_in_percent = ""
    slow_approx_factor_in_percent = ""
    loop_interval_in_seconds = ""
    set_limit_delay_in_seconds = ""
    set_limit_timeout_seconds = ""
    set_limit_delay_in_seconds_multiple_inverter = ""
    poll_interval_in_seconds = ""
    on_grid_usage_jump_to_limit_percent = ""
    max_difference_between_limit_and_outputpower = ""
    set_limit_retry = ""
    set_power_status_delay_in_seconds = ""
    enable_search_modbus_rtu_device = ""
    modhopper1 = ""
    modhopper2 = ""
    modhopper_key = ""
    modhopper_rf_config = ""
    modhopper_rf_channel = ""
    mqtt_broker_cloud = ""
    mqtt_port_cloud = ""
    mqtt_username_cloud = ""
    mqtt_password_cloud = ""
    status = ""
    
    query = "SELECT * FROM `project_setup`"
    result = await MySQL_Select_v1(query) 
    name = result[0]['name']
    serial_number = result[0]['serial_number']
    location = result[0]['location']
    description = result[0]['description']
    administrative_contact = result[0]['administrative_contact']
    id_first_page_on_login = result[0]['id_first_page_on_login']
    id_logging_interval = result[0]['id_logging_interval']
    id_scheduled_upload_time = result[0]['id_scheduled_upload_time']
    number_times_retry = result[0]['number_times_retry']
    id_time_wait_before_retry = result[0]['id_time_wait_before_retry']
    id_upload_debug_information = result[0]['id_upload_debug_information']
    enable_upload_data_on_alarm_status = result[0]['enable_upload_data_on_alarm_status']
    enable_upload_data_on_low_disk = result[0]['enable_upload_data_on_low_disk']
    enable_upload_data_on_system_startup = result[0]['enable_upload_data_on_system_startup']
    link_remote_access = result[0]['link_remote_access']
    allow_remote_access = result[0]['allow_remote_access']
    enable_static_routing = result[0]['enable_static_routing']
    mode = result[0]['mode']
    id_time_zone = result[0]['id_time_zone']
    Time1cycle = result[0]['Time1cycle']
    sampling_time1cycle = result[0]['sampling_time1cycle']
    enable_zero_export = result[0]['enable_zero_export']
    value_zero_export = result[0]['value_zero_export']
    enable_power_limit = result[0]['enable_power_limit']
    value_power_limit = result[0]['value_power_limit']
    powermeter_target_point = result[0]['powermeter_target_point']
    powermeter_tolerance = result[0]['powermeter_tolerance']
    powermeter_max_point = result[0]['powermeter_max_point']
    slow_approx_limit_in_percent = result[0]['slow_approx_limit_in_percent']
    slow_approx_factor_in_percent = result[0]['slow_approx_factor_in_percent']
    loop_interval_in_seconds = result[0]['loop_interval_in_seconds']
    set_limit_delay_in_seconds = result[0]['set_limit_delay_in_seconds']
    set_limit_timeout_seconds = result[0]['set_limit_timeout_seconds']
    set_limit_delay_in_seconds_multiple_inverter = result[0]['set_limit_delay_in_seconds_multiple_inverter']
    poll_interval_in_seconds = result[0]['poll_interval_in_seconds']
    on_grid_usage_jump_to_limit_percent = result[0]['on_grid_usage_jump_to_limit_percent']
    max_difference_between_limit_and_outputpower = result[0]['max_difference_between_limit_and_outputpower']
    set_limit_retry = result[0]['set_limit_retry']
    set_power_status_delay_in_seconds = result[0]['set_power_status_delay_in_seconds']
    enable_search_modbus_rtu_device = result[0]['enable_search_modbus_rtu_device']
    modhopper1 = result[0]['modhopper1']
    modhopper2 = result[0]['modhopper2']
    modhopper_key = result[0]['modhopper_key']
    modhopper_rf_config = result[0]['modhopper_rf_config']
    modhopper_rf_channel = result[0]['modhopper_rf_channel']
    mqtt_broker_cloud = result[0]['mqtt_broker_cloud']
    mqtt_port_cloud = result[0]['mqtt_port_cloud']
    mqtt_username_cloud = result[0]['mqtt_username_cloud']
    mqtt_password_cloud = result[0]['mqtt_password_cloud']
    value_offset_power_limit = result[0]['value_offset_power_limit']
    status = result[0]['status']
    
    if result:
        try:
            current_time = get_utc()
            data_send = {
                    "name":name,
                    "serial_number":serial_number,
                    "location":location,
                    "description":description,
                    "administrative_contact":administrative_contact,
                    "id_first_page_on_login":id_first_page_on_login,
                    "id_logging_interval":id_logging_interval,
                    "id_scheduled_upload_time":id_scheduled_upload_time,
                    "number_times_retry":number_times_retry,
                    "id_time_wait_before_retry":id_time_wait_before_retry,
                    "id_upload_debug_information":id_upload_debug_information,
                    "enable_upload_data_on_alarm_status":enable_upload_data_on_alarm_status,
                    "enable_upload_data_on_low_disk":enable_upload_data_on_low_disk,
                    "enable_upload_data_on_system_startup":enable_upload_data_on_system_startup,
                    "link_remote_access":link_remote_access,
                    "allow_remote_access":allow_remote_access,
                    "enable_static_routing":enable_static_routing,
                    "mode":mode,
                    "id_time_zone":id_time_zone,
                    "Time1cycle":Time1cycle,
                    "sampling_time1cycle":sampling_time1cycle,
                    "enable_zero_export":enable_zero_export,
                    "value_zero_export":value_zero_export,
                    "enable_power_limit":enable_power_limit,
                    "value_power_limit":value_power_limit,
                    "value_offset_power_limit":value_offset_power_limit,
                    "powermeter_target_point":powermeter_target_point,
                    "powermeter_tolerance":powermeter_tolerance,
                    "powermeter_max_point":powermeter_max_point,
                    "slow_approx_limit_in_percent":slow_approx_limit_in_percent,
                    "slow_approx_factor_in_percent":slow_approx_factor_in_percent,
                    "loop_interval_in_seconds":loop_interval_in_seconds,
                    "set_limit_delay_in_seconds":set_limit_delay_in_seconds,
                    "set_limit_timeout_seconds":set_limit_timeout_seconds,
                    "set_limit_delay_in_seconds_multiple_inverter":set_limit_delay_in_seconds_multiple_inverter,
                    "poll_interval_in_seconds":poll_interval_in_seconds,
                    "on_grid_usage_jump_to_limit_percent":on_grid_usage_jump_to_limit_percent,
                    "max_difference_between_limit_and_outputpower":max_difference_between_limit_and_outputpower,
                    "set_limit_retry":set_limit_retry,
                    "set_power_status_delay_in_seconds":set_power_status_delay_in_seconds,
                    "enable_search_modbus_rtu_device":enable_search_modbus_rtu_device,
                    "modhopper1":modhopper1,
                    "modhopper2":modhopper2,
                    "modhopper_key":modhopper_key,
                    "modhopper_rf_config":modhopper_rf_config,
                    "modhopper_rf_channel":modhopper_rf_channel,
                    "mqtt_broker_cloud":mqtt_broker_cloud,
                    "mqtt_port_cloud":mqtt_port_cloud,
                    "mqtt_username_cloud":mqtt_username_cloud,
                    "mqtt_password_cloud" :mqtt_password_cloud,
                    "status" : status,
                    "mqtt": [
                    {"time_stamp" : current_time},
                    {"status":200}]
                    }
        
            push_data_to_mqtt(mqtt_host,
                    mqtt_port,
                    topic ,
                    mqtt_username,
                    mqtt_password,
                    data_send)
        except Exception as err:
            print(f"Error MQTT subscribe: '{err}'")
    else :
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
    result = []
    try:
        
        result_set = mqtt_result.get('parameter', {})
        result_set.pop('mqtt', None)

        if result_set:
            update_fields = ", ".join([f"{field} = %s" for field, value in result_set.items()])
            update_values = [value for field, value in result_set.items()]
            values = [tuple(update_values)]
            query = f"""
            UPDATE project_setup
            SET {update_fields}
            """
            if query and values:
                try:
                    result = MySQL_Update_v2(query, values)

                    if result != None:
                        current_time = get_utc()
                        data_send = {
                            "status": 200,
                            "time_stamp": current_time
                        }
                        push_data_to_mqtt(mqtt_host,
                                            mqtt_port,
                                            topic,
                                            mqtt_username,
                                            mqtt_password,
                                            data_send)
                    else:
                        current_time = get_utc()
                        data_send = {
                            "status": 400,
                            "time_stamp": current_time
                        }
                        push_data_to_mqtt(mqtt_host,
                                            mqtt_port,
                                            topic,
                                            mqtt_username,
                                            mqtt_password,
                                            data_send)
                except Exception as err:
                    print(f"Error updating database: '{err}'")
                    
        else:
            print("result_set is empty, skipping update")
            current_time = get_utc()
            data_send = {
                "status": 200,
                "time_stamp": current_time
            }
            push_data_to_mqtt(mqtt_host,
                                mqtt_port,
                                topic,
                                mqtt_username,
                                mqtt_password,
                                data_send)
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
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
        print(f"Error MQTT subscribe: '{err}'") 
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
    result_pmax_custom = []
    result_pmax = []
    result_pmin_percent = []
    p_max_custom = 0
    p_max = 0
    p_min_percent = 0
    p_min = 0
    value_array = []
    operator_array = []
    value = 0
    operator = 0
    if mqtt_result and isinstance(mqtt_result, list):
        for item in mqtt_result:
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                status_device = item['status_device']
                
                value_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "ControlINV"]
                operator_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "OperatingState"]
                if value_array:
                    value = value_array[0]
                if operator_array:
                    operator = operator_array[0]
                if await check_inverter_device(id_device) and status_device == 'online' and mode == 1 and operator not in [7, 8]:
                    
                    # Pmax custom
                    result_pmax_custom = MySQL_Select("SELECT rated_power_custom FROM `device_list` WHERE id = %s", (id_device,))
                    p_max_custom = result_pmax_custom[0]["rated_power_custom"]
                    
                    # Pmax
                    result_pmax = MySQL_Select("SELECT rated_power FROM `device_list` WHERE id = %s", (id_device,))
                    p_max = result_pmax[0]["rated_power"]
                    
                    # Pmax
                    result_pmin_percent = MySQL_Select("SELECT min_watt_in_percent FROM `device_list` WHERE id = %s", (id_device,))
                    p_min_percent = result_pmin_percent[0]["min_watt_in_percent"]
                    
                    if p_max and p_min_percent:
                        p_min = (p_max*p_min_percent)/100
                        
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
        print("device_list",device_list)
    return device_list
# Describe get_value_meter 
# 	 * @description get_value_meter
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return value_production ,value_consumption
# 	 */ 
async def get_value_meter():
    global result_topic4
    value_production_aray = []
    value_consumption_aray = []
    total_value_production = 0
    total_value_consumption = 0
    global value_production
    global value_consumption

    if result_topic4:
        for item in result_topic4:
            if 'id_device' in item:
                id_device = item['id_device']
                result_type_meter = MySQL_Select("SELECT `device_type`.`name` FROM `device_type` INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id WHERE `device_list`.id = %s", (id_device,))
                
                if result_type_meter:
                    if result_type_meter[0]["name"] == "Production Meter":
                        value_production_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if len(value_production_aray) > 0 and value_production_aray[0] is not None:
                            total_value_production += value_production_aray[0]
                            value_production = total_value_production
                    elif result_type_meter[0]["name"] == "Consumption meter":
                        value_consumption_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if len(value_consumption_aray) > 0 and value_consumption_aray[0] is not None:
                            total_value_consumption += value_consumption_aray[0]
                            value_consumption = total_value_consumption
                else:
                    pass
        # end for 
    else:
        pass  
# Describe process_caculator_p_power_limit 
# 	 * @description process_caculator_p_power_limit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return p_for_each_device_power_limit
# 	 */ 
async def process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4
    global enable_power_limit
    global enable_zero_export
    global value_power_limit
    global devices
    global value_cumulative
    global value_subcumulative
    global value_production
    global total_power
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    global p_for_each_device_power_limit
    efficiency_total = 0
    id_device = 0
    result_slope = []
    slope = 1
    power_max = 0
    power_max_convert = 0
    p_max_real = 0
    delta = 1
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)
    else:
        pass

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
                    
            if power_max and slope:
                if total_power and value_power_limit:  
                    # difference coefficient between actual and value in inv 333 with 3330 = 0.1
                    delta = slope*1000
                    power_max_convert = ((power_max/slope)*delta)
                    p_max_real = ((total_power/slope)*delta)
                    efficiency_total = (value_power_limit/p_max_real)

                    if efficiency_total > 1 :
                        efficiency_total = 1
                    else:
                        pass
                else:
                    pass
                
                p_for_each_device_power_limit = (efficiency_total*power_max_convert)/delta
                
                if p_for_each_device_power_limit > power_max_convert/delta:
                    p_for_each_device_power_limit = power_max_convert/delta
                else:
                    pass
            
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
            else:
                pass
            device_list_control_power_limit.append(new_device)

        if len(devices) == len(device_list_control_power_limit) and enable_zero_export == 0 :
            push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            print("Value setpoint",value_power_limit)
            print("P Feedback production",value_production)
            print("P Feedback consumption",value_consumption)
    
            p_for_each_device_power_limit = 0
        else:
            pass
    else:
        pass
# Describe process_caculator_zero_export 
# 	 * @description process_caculator_zero_export
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password}
# 	 * @return p_for_each_device_zero_export
# 	 */ 
async def process_caculator_zero_export(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4
    global enable_power_limit
    global value_zero_export
    global value_consumption
    global devices
    global value_cumulative
    global value_subcumulative
    global value_production
    global total_power
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    efficiency_total = 0
    power_max = 0
    id_device = 0
    result_slope = []
    slope = 1.0
    power_max_convert = 0
    p_max_real = 0
    delta = 1
    global p_for_each_device_zero_export 
    total_p_inv_prodution = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    if value_consumption > 0 :
        value_consumption = value_consumption - (value_consumption*value_zero_export/100)
    else:
        value_consumption = 0
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

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
                    
            if power_max and slope:
                if total_power and value_consumption :  
                    # difference coefficient between actual and value in inv 333 with 3330 = 0.1
                    delta = slope*1000
                    power_max_convert = ((power_max/slope)*delta)
                    p_max_real = ((total_power/slope)*delta)
                    efficiency_total = (value_consumption/p_max_real)
                    
                    if efficiency_total > 1 :
                        efficiency_total = 1
                    else:
                        pass
                if efficiency_total:
                    p_for_each_device_zero_export = (efficiency_total*power_max_convert)/delta
                
                if p_for_each_device_zero_export > power_max_convert/delta:
                    p_for_each_device_zero_export = power_max_convert/delta
                else:
                    pass
            
            if p_for_each_device_zero_export <= 0 :
                p_for_each_device_zero_export = 0 
            else:
                pass

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
    global result_topic4
    global enable_power_limit
    global value_zero_export
    global value_consumption
    global devices
    global value_cumulative
    global value_subcumulative
    global value_production
    global total_power
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    global p_for_each_device_zero_export
    global p_for_each_device_power_limit
    
    p_for_each_device = 0
    total_p_inv_prodution = 0
    power_max_convert = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    await process_caculator_zero_export(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
    await process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password)
    
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
            
            if power_max and slope:
                if total_power and value_consumption :  
                    # difference coefficient between actual and value in inv 333 with 3330 = 0.1
                    delta = slope*1000
                    power_max_convert = ((power_max/slope)*delta)
            
            if p_for_each_device_zero_export and p_for_each_device_power_limit :
                p_for_each_device = p_for_each_device_zero_export + p_for_each_device_power_limit
            if p_for_each_device > power_max_convert/delta:
                    p_for_each_device = power_max_convert/delta
            else:
                pass

            print("Value setpoint",p_for_each_device)
            print("P Feedback production",value_production)
            print("P Feedback consumption",value_consumption)
            print("Value INV Out",p_for_each_device)
            
            total_p_inv_prodution += p_for_each_device
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
        
        if value_consumption < total_p_inv_prodution :
            new_device = {
                    "id_device": device["id_device"],
                    "mode": device["mode"],
                    "status": "zero export + power limit",
                    "setpoint": value_consumption + value_power_limit,
                    "parameter": [
                        {"id_pointkey": "WMax", "value": 0}
                    ]
                }
            push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            
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
    global result_topic4
    global devices
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    power_max = 0
    result_slope = []
    slope = 1.0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    p_for_each_device = 0
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    if devices :
            device_list_control_power_limit = []
            for device in devices:
                id_device = device["id_device"]
                power_max = device["p_max"]
                power_max = float(power_max)
                
                if id_device :
                    result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`name` = 'Power Limit' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s ", (id_device,))
                if result_slope :
                    slope = float(result_slope[0]["slope"])
                    
                if power_max and slope :
                    p_for_each_device = power_max/slope
                        
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
    
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
    global percent_offset_power_limit 
    global percent_offset_zero_export 
    global MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
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
    
    try:
        if mqtt_result and 'mode' in mqtt_result and 'type' in mqtt_result and 'enable' in mqtt_result and 'value' in mqtt_result:
            mode_auto = mqtt_result['mode'] 
            type_mode_auto = mqtt_result['type']
            bitchecktopic3 = 1
            
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
        print(f"Error MQTT subscribe: '{err}'")
# Describe process_getfirst_zeroexport_powerlimit 
# 	 * @description process_getfirst_zeroexport_powerlimit
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return enable_zero_export ,value_zero_export,enable_power_limit,value_power_limit
# 	 */ 
async def process_getfirst_zeroexport_powerlimit():
    
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
    value_power_limit_temp = 0
    global percent_offset_power_limit 
    result_project_setup = []
    
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
        print(f"Error MQTT subscribe: '{err}'")   
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
    
    if enable_zero_export == 1 and enable_power_limit == 0:
        print("==============================zero_export==============================")
        await process_caculator_zero_export(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    elif enable_power_limit == 1 and value_power_limit != 0 and enable_zero_export == 0:
        print("==============================power_limit==============================")
        await process_caculator_p_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password)
    elif ( enable_zero_export == 1 and value_zero_export != 0 ) and (enable_power_limit == 1 and value_power_limit != 0):
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
        elif topic == topic5:
            result_topic5 = message
        elif topic == topic6:
            result_topic6 = message
            await insert_information_project_setup_when_request(result_topic6,serial_number_project, host, port, username, password)
            print("result_topic6",result_topic6)
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
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