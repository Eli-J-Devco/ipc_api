import logging
import os
import sys
import mqttools
import asyncio
import json
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

value_production = 0
value_consumption = 0
value_cumulative = 0
value_subcumulative = 0

total_power = 0

result_topic4 = []
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
MQTT_TOPIC_SUD_MODEGET_INFORMATION = "/Project/Get"
MQTT_TOPIC_SUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto"
MQTT_TOPIC_PUD_CHOICES_MODE_AUTO = "/Control/Setup/Auto/Feedback"
MQTT_TOPIC_SUD_DEVICES_ALL = "/Devices/All"
MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT = "/Control/Write"

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

async def pud_confirm_mode_control(serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    global ModeSysTemp
    global flag 
    result = []
    topic = serial_number_project + topicPublic 
    if not ModeSysTemp and flag == 0:
        query = "SELECT `project_setup`.`mode` FROM `project_setup`"
        result = await MySQL_Select_v1(query) 
        ModeSysTemp = result[0]['mode']
    
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
async def process_update_mode_for_device_for_systemp(mqtt_result):
    
    global ModeSysTemp
    try:
        if mqtt_result:
            try:
                if mqtt_result.get('id_device') == 'Systemp':
                    ModeSysTemp = mqtt_result.get('mode')  

                    querysystemp = "UPDATE `project_setup` SET `project_setup`.`mode` = %s;"
                    querydevice = "UPDATE device_list JOIN device_type ON device_list.id_device_type = device_type.id SET device_list.mode = %s WHERE device_type.name = 'PV System Inverter';;"

                    if ModeSysTemp in [0, 1, 2]:
                        MySQL_Insert_v5(querysystemp, (ModeSysTemp,))
                    else :
                        print("Failed to insert data")
                    if ModeSysTemp in [0, 1]:
                        MySQL_Insert_v5(querydevice, (ModeSysTemp,))
                    else:
                        pass
            except Exception as json_err:
                print(f"Error processing JSON data: {json_err}")
        else:
            print("Received empty or invalid JSON data from MQTT")
            
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
async def pud_feedback_project_setup(serial_number_project, mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
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
    
    if result:
        try:
            current_time = get_utc()
            data_send = {
                    "status" : 200,
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
                    "time_stamp" : current_time
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
async def pud_information_project_setup_when_request(mqtt_result ,serial_number_project,host, port, username, password):
    global MQTT_TOPIC_PUD_PROJECT_SETUP
    topicpud = serial_number_project + MQTT_TOPIC_PUD_PROJECT_SETUP
    try:
        if mqtt_result and 'get_information' in mqtt_result:
            await pud_feedback_project_setup(serial_number_project,
                                                host,
                                                port,
                                                topicpud,
                                                username,
                                                password)                       
        else:
            pass
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'") 
async def check_inverter_device(device_control):
    results_device_type = []
    
    query = "SELECT `device_type`.`name` FROM device_type INNER JOIN `device_list` ON device_list.id_device_type=device_type.id WHERE device_list.id=%s;"
    results_device_type = MySQL_Select(query, (device_control,))
    if results_device_type and results_device_type[0]["name"] == "PV System Inverter":
        return True  
    else:
        return False  
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
async def get_value_meter():
    global result_topic4
    value_production_aray = []
    value_consumption_aray = []
    global value_production
    global value_consumption

    if result_topic4:
        for item in result_topic4:
            if 'id_device' in item:
                id_device = item['id_device']
                result_type_meter = MySQL_Select("SELECT `device_type`.`name` FROM `device_type` INNER JOIN `device_list` ON `device_list`.`id_device_type` = `device_type`.id WHERE `device_list`.id = %s", (id_device,))
                
                value_production_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                
                if result_type_meter:
                    if result_type_meter[0]["name"] == "Production Meter":
                        value_production_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if value_production_aray :
                            value_production += value_production_aray[0]
                            print("P san xuat",value_production)
                    elif result_type_meter[0]["name"] == "Consumption meter":
                        value_consumption_aray = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "TotalActivePower"]
                        if value_production_aray :
                            value_consumption += value_consumption_aray[0]
                            print("P tieu thu",value_consumption)
        # end for 
        value_production_aray = []
        value_consumption_aray = []
    else:
        pass  
async def process_caculator_p_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4
    global enable_power_limit
    global value_power_limit
    global devices
    global value_cumulative
    global value_subcumulative
    global value_production
    global total_power
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    efficiency_total = 0
    power_max = 0
    power_min = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    print("gia tri setpoint",value_power_limit)
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    if devices :
        if total_power and value_power_limit:  
            efficiency_total = value_power_limit/total_power
            if efficiency_total > 1 :
                efficiency_total = 1
            device_list_control_power_limit = []
            for device in devices:
                power_max = device["p_max"]
                power_min = device["p_min"]
                power_max = int(power_max)
                
                if efficiency_total and power_max:
                    p_for_each_device = efficiency_total*power_max
                    if p_for_each_device > power_max:
                        p_for_each_device = power_max
                    if p_for_each_device <= power_min:
                        p_for_each_device = power_min
                
                print(f"gia tri dieu khien {p_for_each_device} cho thiet bi {device['id_device']}")
                
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                device_list_control_power_limit.append(new_device)

            if len(devices) == len(device_list_control_power_limit):
                push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            else:
                pass
        else:
            pass
    else:
        pass 
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
    power_min = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    print("gia tri setpoint",value_zero_export)
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    if devices :
        if total_power and value_consumption:  
            efficiency_total = value_consumption/total_power
            if efficiency_total > 1 :
                efficiency_total = 1
                
        elif value_consumption == 0 :
            efficiency_total = 0

            device_list_control_power_limit = []
            for device in devices:
                power_max = device["p_max"]
                power_max = int(power_max)
                
                if efficiency_total and power_max:
                    p_for_each_device = efficiency_total*power_max
                    if p_for_each_device > power_max:
                        p_for_each_device = power_max
                        
                elif efficiency_total == 0 :
                    p_for_each_device = 0
                    
                print(f"gia tri dieu khien {p_for_each_device} cho thiet bi {device["id_device"]}")
                
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                device_list_control_power_limit.append(new_device)

            if len(devices) == len(device_list_control_power_limit):
                push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            else:
                pass
        else:
            pass
    else:
        pass 
async def process_caculator_zero_export_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4
    global enable_power_limit
    global value_zero_export
    global value_power_limit
    global devices
    global value_cumulative
    global value_subcumulative
    global value_production
    global total_power
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    value_total = 0
    efficiency_total = 0
    power_max = 0
    power_min = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    if value_power_limit and value_production :
        value_total = value_power_limit + value_production
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    if devices :
        if total_power and value_total:  
            efficiency_total = value_total/total_power
            if efficiency_total > 1 :
                efficiency_total = 1
            device_list_control_power_limit = []
            for device in devices:
                power_max = device["p_max"]
                power_min = device["p_min"]
                power_max = int(power_max)
                
                if efficiency_total and power_max:
                    p_for_each_device = efficiency_total*power_max
                    if p_for_each_device > power_max:
                        p_for_each_device = power_max
                    if p_for_each_device <= power_min:
                        p_for_each_device = power_min
                        
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                device_list_control_power_limit.append(new_device)

            if len(devices) == len(device_list_control_power_limit):
                push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            else:
                pass
        else:
            pass
    else:
        pass 
async def process_not_choose_zero_export_power_limit(serial_number_project, mqtt_host, mqtt_port, mqtt_username, mqtt_password):
    global result_topic4
    global devices
    global MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    power_max = 0
    topicpud = serial_number_project + MQTT_TOPIC_PUD_CONTROL_POWER_LIMIT
    
    if result_topic4:
        devices = await get_list_device_in_automode(result_topic4)

    if devices :
            device_list_control_power_limit = []
            for device in devices:
                power_max = device["p_max"]
                power_max = int(power_max)
                
                if power_max:
                    p_for_each_device = power_max
                        
                if device['controlinv'] == 1:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                else:
                    new_device = {
                        "id_device": device["id_device"],
                        "mode": device["mode"],
                        "parameter": [
                            {"id_pointkey": "ControlINV", "value": 1},
                            {"id_pointkey": "WMax", "value": p_for_each_device}
                        ]
                    }
                device_list_control_power_limit.append(new_device)

            if len(devices) == len(device_list_control_power_limit):
                push_data_to_mqtt( mqtt_host, mqtt_port, topicpud, mqtt_username, mqtt_password, device_list_control_power_limit)
            else:
                pass
    else:
        pass 
async def process_update_zeroexport_powerlimit(mqtt_result,serial_number_project, mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password ):
    
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
    global MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
    bitchecktopic3 = 0
    
    topicPudModeAuto = serial_number_project + MQTT_TOPIC_PUD_CHOICES_MODE_AUTO
    
    current_time = get_utc()
    mode_auto = ""
    type_mode_auto = ""
    comment = 0
    
    try:
        if mqtt_result and 'mode' in mqtt_result and 'type' in mqtt_result and 'enable' in mqtt_result and 'value' in mqtt_result:
            mode_auto = mqtt_result['mode'] 
            type_mode_auto = mqtt_result['type']
            bitchecktopic3 = 1
            
            if mode_auto == "zero_export":
                if type_mode_auto == "checkbox":
                    enable_zero_export = mqtt_result.get('enable', enable_zero_export)
                    if enable_zero_export is not None:
                        MySQL_Update_V1("update project_setup set enable_zero_export = %s", (enable_zero_export,))
                elif type_mode_auto == "textbox":
                    value_zero_export = mqtt_result.get('value', value_zero_export)
                    if value_zero_export is not None:
                        MySQL_Update_V1("update project_setup set value_zero_export = %s", (value_zero_export,))
            elif mode_auto == "power_limit":
                if type_mode_auto == "checkbox":
                    enable_power_limit = mqtt_result.get('enable', enable_power_limit)
                    if enable_power_limit is not None:
                        MySQL_Update_V1("update project_setup set enable_power_limit = %s", (enable_power_limit,))
                elif type_mode_auto == "textbox":
                    value_power_limit = mqtt_result.get('value', value_power_limit)
                    if value_power_limit is not None:
                        MySQL_Update_V1("update project_setup set value_power_limit = %s", (value_power_limit,))
            # When you receive one of the above information, give feedback to mqtt
            if ( enable_zero_export or value_zero_export or enable_power_limit or value_power_limit ) and bitchecktopic3 == 1 :
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
async def process_getfirst_zeroexport_powerlimit():
    
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
    result_project_setup = []
    
    try:
        result_project_setup = await MySQL_Select_v1("select * from project_setup")
        if result_project_setup :
            enable_zero_export = result_project_setup[0]["enable_zero_export"]
            value_zero_export = result_project_setup[0]["value_zero_export"]
            enable_power_limit = result_project_setup[0]["enable_power_limit"]
            value_power_limit = result_project_setup[0]["value_power_limit"]
        
        else:
            pass
            
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")   
async def process_zero_export_power_limit(serial_number_project,mqtt_host ,mqtt_port ,mqtt_username ,mqtt_password):
    global enable_zero_export
    global value_zero_export
    global enable_power_limit
    global value_power_limit
    
    if enable_zero_export == 1 and value_zero_export != 0 and enable_power_limit == 0:
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
async def sub_mqtt(serial_number_project, host, port, topic1, topic2,topic3,topic4, username, password):
    
    result_topic1 = ""
    result_topic2 = ""
    result_topic3 = ""
    global result_topic4
    
    topic1 = serial_number_project + topic1
    topic2 = serial_number_project + topic2
    topic3 = serial_number_project + topic3
    topic4 = serial_number_project + topic4
    
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topic1)
        await client.subscribe(topic2)
        await client.subscribe(topic3)
        await client.subscribe(topic4)
        
        while True:
            try:
                message = await asyncio.wait_for(client.messages.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            if message.topic == topic1:
                result_topic1 = json.loads(message.message.decode())
                await process_update_mode_for_device_for_systemp (result_topic1)
            elif message.topic == topic2:
                result_topic2 = json.loads(message.message.decode())
                await pud_information_project_setup_when_request(result_topic2,serial_number_project, host, port, username, password)
            elif message.topic == topic3:
                result_topic3 = json.loads(message.message.decode())
                await process_update_zeroexport_powerlimit(result_topic3,serial_number_project,host, port, username, password)
            elif message.topic == topic4:
                result_topic4 = json.loads(message.message.decode())
                # await get_list_device_in_automode(result_topic4)
                
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")

async def main():
    tasks = []
    await process_getfirst_zeroexport_powerlimit()
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    serial_number_project=results_project[0]["serial_number"]
    tasks.append(asyncio.create_task(sub_mqtt(serial_number_project,
                                                    MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
                                                    MQTT_TOPIC_SUD_MODEGET_INFORMATION,
                                                    MQTT_TOPIC_SUD_CHOICES_MODE_AUTO,
                                                    MQTT_TOPIC_SUD_DEVICES_ALL,
                                                    MQTT_USERNAME,
                                                    MQTT_PASSWORD
                                                    )))
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(pud_confirm_mode_control, 'cron',  second = f'*/1' , args=[serial_number_project,
                                                                        MQTT_BROKER,
                                                                        MQTT_PORT,
                                                                        MQTT_TOPIC_PUD_FEEDBACK_MODECONTROL,
                                                                        MQTT_USERNAME,
                                                                        MQTT_PASSWORD])
    scheduler.add_job(process_zero_export_power_limit, 'cron',  minute = f'*/1' , args=[serial_number_project,
                                                                        MQTT_BROKER,
                                                                        MQTT_PORT,
                                                                        MQTT_USERNAME,
                                                                        MQTT_PASSWORD])
    scheduler.add_job(get_value_meter, 'cron',  second = f'*/10' , args=[])
    scheduler.start()
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())