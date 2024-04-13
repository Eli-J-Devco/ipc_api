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
async def pud_information_project_setup_when_request(mqtt_result ,serial_number_project,host, port, username, password):
    global MQTT_TOPIC_PUD_PROJECT_SETUP
    topicpud = serial_number_project + MQTT_TOPIC_PUD_PROJECT_SETUP
    print("topicpud", topicpud)
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

async def sud_mqtt(serial_number_project, host, port, topic1, topic2, username, password):
    
    result_topic1 = ""
    result_topic2 = ""
    
    topic1 = serial_number_project + topic1
    topic2 = serial_number_project + topic2
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topic1)
        await client.subscribe(topic2)
        
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
                
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
        
async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    serial_number_project=results_project[0]["serial_number"]
    tasks.append(asyncio.create_task(sud_mqtt(serial_number_project,
                                                    MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC_SUD_MODECONTROL_DEVICE,
                                                    MQTT_TOPIC_SUD_MODEGET_INFORMATION,
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
    
    scheduler.start()
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())