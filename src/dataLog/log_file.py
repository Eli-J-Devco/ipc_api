# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import asyncio
import datetime
import json
import os
import re
import sys
import time

import mqttools
import mybatis_mapper2sql
import paho.mqtt.publish as publish
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMySQL import *

# from config import *
# from test.libMySQL import *

# Use passing parameters to file
arr = sys.argv
# print(f'arr: {arr}')
# ------------------------------------
result_list =[]
status_device = ""     
msg_device = ""
status_register = ""
status_file = "Success"
value_many = []
value_dict = []
data_mqtt = ""
sql_id_str = ""
device_name = ""
file_name = ""
flag_mqtt = False
count_mqtt = 0
data_in_file = ""
formatted_time1 = ""
time_interval = ""
QUERY_TIME_SYNC_DATA=""
QUERY_ALL_DEVICES=""
QUERY_INSERT_SYNC_DATA=""
QUERY_INSERT_SYNC_DATA_EXECUTEMANY=""
QUERY_SELECT_COUNT_POINT_LIST=""

result_all = []
time_create_file_insert_data_table_dev = ""

# Variables 
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC_SUB = Config.MQTT_TOPIC + "/Dev/#"
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/CreateLogFile" 
MQTT_USERNAME = Config.MQTT_USERNAME 
MQTT_PASSWORD = Config.MQTT_PASSWORD

DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_USERNAME = Config.DATABASE_USERNAME
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME

FOLDER_PATH = Config.FOLDER_PATH_LOG
HEAD_FILE_LOG = Config.HEAD_FILE_LOG

#----------------------------------------
# /**
# 	 * @description find path directory relative
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {project_name}
# 	 * @return result
# 	 */
def path_directory_relative(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    print("Path directory relative:", result)
    return result
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+file_name)
    statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
    result={}
    for item,value in enumerate(statement):
        for key in value.keys():
            result[key]=value[key]   

    return result  
#----------------------------------------
# /**
# 	 * @description take time 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {}
# 	 * @return datetime
# 	 */
def get_utc():
    now=None
    try:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if now:
            return now
    except Exception as err:
        return None
# ----- MQTT -----
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
def push_data_to_mqtt(host, port,topic, username, password, data_send):
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                    retain=False, port=port,
                    auth = {'username':f'{username}', 
                            'password':f'{password}'})
        # publish.single(Topic, payload, hostname=Broker,
        #             retain=False, port=Port)
    # except Error as err:
    #     print(f"Error MQTT public: '{err}'")
    except Exception as err:
    # except:
        
        print(f"Error MQTT public: '{err}'")
        pass
#--------------------------------------------------------------------
# /**
# 	 * @description subscribe data from MQTT
# 	 * @author bnguyen
# 	 * @since 05-12-2023
# 	 * @param {host, port, topic, username, password}
# 	 * @return result_list 
# 	 */ 
async def Get_MQTT(host, port, topic, username, password):
    global status_device    
    global msg_device 
    global status_register
    global result_list
    global status_file
    result_values_dict = {}
    result_value = []
    result_point_id = []
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client :
            print("Error connect with MQTT")
            return -1 
        await client.start()
        await client.subscribe(topic)
        while True:
            current_time = get_utc()
            message = await client.messages.get()
            if not message :
                print("Not find message from MQTT")
                return -1 
            # cut string get device id value from sud mqtt
            cut_topic1 = message.topic[8:]
            device_id = cut_topic1.split("|")[0]
            
            if status_file == "Success" :
                result_value = []
                result_point_id = []
            else :
                result_value == result_values_dict
                
            mqtt_result = json.loads(message.message.decode())
            if mqtt_result:
                if 'STATUS_DEVICE' not in mqtt_result:
                    return -1 
                if 'MSG_DEVICE' not in mqtt_result:
                    return -1 
                if 'STATUS_REGISTER' not in mqtt_result:
                    return -1 
                if 'POINT_LIST' not in mqtt_result:
                    return -1 
                status_device = mqtt_result['STATUS_DEVICE']        
                msg_device = mqtt_result['MSG_DEVICE']
                status_register = mqtt_result['STATUS_REGISTER']
                
                for item in mqtt_result['POINT_LIST']:
                    value = str(item["Value"])
                    point_id = str(item["ItemID"])
                                
                    result_value.append(value)
                    result_point_id.append(point_id)
                                
                result_values_dict[device_id] = result_value, result_point_id
                result_list = [
                    {"id": int(device_id), "point_id": point_id, "data": values, "time": current_time}
                    for device_id, (values, point_id) in result_values_dict.items()
                ]
            else: 
                pass
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
#--------------------------------------------------------------------
# /**
# 	 * @description 
#       - create and write data in file  
#       - sync data file with database 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port, topic, username, password}
# 	 * @return result_list 
# 	 */ 
async def Create_Filelog(sql_id,base_path,id_device,head_file,host, port, topic, username, password):

    id_device_fr_sys = id_device[1]
    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    global QUERY_TIME_SYNC_DATA
    global QUERY_SELECT_COUNT_POINT_LIST
    global QUERY_INSERT_SYNC_DATA
    
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    array_count_point = MySQL_Select(QUERY_SELECT_COUNT_POINT_LIST,(id_device_fr_sys,))
    count = array_count_point[0]['COUNT(*)']
    #---------------------------------------------------------------------------------------------------------------
    current_time = get_utc()
    current_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    year,month, day = current_datetime.year , current_datetime.month,current_datetime.day
    global status_device    
    global msg_device 
    global status_register
    global result_list
    global status_file
    global type_file
    global value_many
    global flag_mqtt
    data_to_write =""
    global data_in_file
    global file_name
    global formatted_time1
    time_online = current_time
    data_insert =""
    data_mqtt = []
    data_mqtts = []
    #-----------------------------------------------------
        
    for item in time_sync_data:
        type_file = item["type_protocol"]
        
    # File creation time 
    sql_id_str = str(sql_id)
    device_name = [item['name'] for item in result_all if item['id'] == sql_id][0]
    modbus_device = [item['rtu_bus_address'] for item in result_all if item['id'] == sql_id][0]
    
    DictID = [item for item in result_list if item["id"] == sql_id]
    
    if DictID:
        data = DictID[0]["data"]
        data_to_write = data
        time_online = DictID[0]["time"]
        
    date_folder_path = os.path.join(base_path, f"{id_device_fr_sys}\\{type_file}\\{sql_id}\\{year}\\{month}\\{day}")
    try:
        os.makedirs(date_folder_path, exist_ok=True)
        time_file = get_utc()
        time_file_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        formatted_time1 = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
        file_name = f'{head_file}-{sql_id:03d}.{formatted_time1}.txt'
        file_path = os.path.join(date_folder_path, file_name)
        source_file = date_folder_path + "/" + file_name
        
        if not data_to_write:
            data_in_file = ["" for i in range(count)]
        else:
            data_in_file = [str(val) for val in data_to_write]

        with open(file_path, 'w') as file:
            formatted_time2 = "'" + time_file + "'"
            file.write(f'{formatted_time2},0,0,0,{",".join(data_in_file)}')
            
            # code write data in table sync data ------------------------------------------------------------------
            time_insert = get_utc()
            if not data_to_write:
                # Handle when data_to_write value does not exist
                data_insert = (time_insert, sql_id, modbus_device, date_folder_path, source_file, file_name, time_insert,f'{formatted_time2},0,0,0,{",".join(data_in_file)}', id_device_fr_sys)
            else:
                data_insert = (time_insert, sql_id, modbus_device, date_folder_path, source_file, file_name, time_insert,f'{formatted_time2},0,0,0,{",".join(data_in_file)}', id_device_fr_sys)
            
            for index, item in enumerate(value_many):
                if item[1] == sql_id:
                    # Update the SQL query
                    value_many[index] = data_insert
                    break
            else:
                # Add a new entry to the list
                value_many.append(data_insert)
                
            # code pud data MQTT ----------------------------------------------------------------- 
            status_file = "Success"
            ts_timestamp = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
            ts_online = datetime.datetime.strptime(time_online, "%Y-%m-%d %H:%M:%S").timestamp()
            if ts_timestamp - ts_online < 10 :
                status_device ="NEW"
            else :
                status_device ="OLD"
                pass
            data_mqtt={
            "ID_DEVICE":sql_id_str,
            "STATUS_DATA":status_device,
            "STATUS_CHANNEL":status_file,
            "FILE_NAME":file_name,
            "Timestamp" :current_time,
            "TimeOnline" :time_online,
            "DATA_LOG":[data_in_file]
            }
            push_data_to_mqtt(host,
                    port,
                    topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str+"|"+device_name,
                    username,
                    password,
                    data_mqtt)
            #----------------------------------------------------------------- 
    except Exception as e:
        status_file = "Fault"
        print(f"Error during file creation is : {e}")
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(sql_id,id_device,head_file,host, port,topic, username, password):
    global flag_mqtt
    global data_mqtt
    global count_mqtt
    global status_device 
    global status_file
    global data_in_file
    global file_name
    global result_list
    global formatted_time1
    global time_interval
    
    current_time = get_utc()
    result_all = []
    data = []
    time_online = current_time

    id_device_fr_sys = id_device[1]
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    sql_id_str = ""
    device_name = ""
    
    for item in time_sync_data:
        type_file = item["type_protocol"]
    
    file_name = f'{head_file}-{sql_id:03d}.{formatted_time1}.txt'
    DictID = [item for item in result_list if item["id"] == sql_id]

    if DictID:
        time_online = DictID[0]["time"]
        data = DictID[0]["data"]    
    try:
        if formatted_time1 :
            data_mqtt={
                "ID_DEVICE":sql_id,
                "STATUS_DATA":status_device,
                "STATUS_CHANNEL":status_file,
                "FILE_NAME":file_name,
                "TIME_STAMP" :current_time,
                "TIME_ONLINE" :time_online,
                "TIME_LOG": time_interval,
                "DATA_LOG":data,
                }
        else :
            status_file = "Fault"
            data_mqtt={
                "ID_DEVICE":sql_id,
                "STATUS_DATA":"loading",
                "STATUS_CHANNEL":status_file,
                "FILE_NAME":"None",
                "TIME_STAMP" :current_time,
                "TIME_ONLINE" :time_online,
                "TIME_LOG": time_interval,
                "DATA_LOG":data,
                }
        # File creation time 
        sql_id_str = str(sql_id)
        device_name = [item['name'] for item in result_all if item['id'] == sql_id][0] 
        push_data_to_mqtt(host,
                port,
                topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str+"|"+device_name,
                username,
                password,
                data_mqtt)
        # status_file = "Success"
    except Exception as err:
        print('Error monitoring_device : ',err)
        
#--------------------------------------------------------------------
# /**
# 	 * @description Insert data to Database
# 	 * @author bnguyen
# 	 * @since 04-01-2024
# 	 * @param {}
# 	 * @return  
# 	 */ 
async def Insert_Sync():
    global QUERY_INSERT_SYNC_DATA_EXECUTEMANY
    global value_many
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    # File creation time 
    if len(value_many) == len(result_all):
        MySQL_Insert_v4(QUERY_INSERT_SYNC_DATA_EXECUTEMANY,value_many)
    else :
        pass

async def main():
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    global QUERY_ALL_DEVICES
    global QUERY_TIME_CREATE_FILE
    global QUERY_TIME_SYNC_DATA
    global QUERY_INSERT_SYNC_DATA
    global QUERY_INSERT_SYNC_DATA_EXECUTEMANY
    global QUERY_SELECT_COUNT_POINT_LIST
    global time_interval
    try:
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_TIME_SYNC_DATA=result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_INSERT_SYNC_DATA_EXECUTEMANY=result_mybatis["QUERY_INSERT_SYNC_DATA_EXECUTEMANY"]
        QUERY_INSERT_SYNC_DATA=result_mybatis["QUERY_INSERT_SYNC_DATA"]
        QUERY_SELECT_COUNT_POINT_LIST=result_mybatis["QUERY_SELECT_COUNT_POINT_LIST"]
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_TIME_CREATE_FILE or not QUERY_ALL_DEVICES or not QUERY_TIME_SYNC_DATA or not QUERY_INSERT_SYNC_DATA or not QUERY_SELECT_COUNT_POINT_LIST or not QUERY_INSERT_SYNC_DATA_EXECUTEMANY:
        print("Error not found data in file mybatis")
        return -1
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    
    if not result_all or not time_create_file_insert_data_table_dev :
        print("Error not found data in Database")
        return -1
    
    item = time_create_file_insert_data_table_dev[0]
    time_interval = item["time_log_interval"]
    position = time_interval.rfind("minute")
    number = time_interval[:position]
    int_number = int(number)
    #-------------------------------------------------------
    scheduler = AsyncIOScheduler()
    for item in result_all:
        sql_id = item["id"]
        scheduler.add_job(Create_Filelog, 'cron',  minute = f'*/{int_number}', args=[sql_id,
                                                                            FOLDER_PATH,
                                                                            arr,
                                                                            HEAD_FILE_LOG,
                                                                            MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_TOPIC_PUB,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
        scheduler.add_job(monitoring_device, 'cron',  second = f'*/7' , args=[ sql_id,
                                                                                arr,
                                                                                HEAD_FILE_LOG,
                                                                                MQTT_BROKER,
                                                                                MQTT_PORT,
                                                                                MQTT_TOPIC_PUB,
                                                                                MQTT_USERNAME,
                                                                                MQTT_PASSWORD])
    scheduler.add_job(Insert_Sync, 'cron',  minute = f'*/{int_number}')
    scheduler.start()
    #-------------------------------------------------------
    tasks = []
    tasks.append(asyncio.create_task(Get_MQTT(MQTT_BROKER,
                                                            MQTT_PORT,
                                                            MQTT_TOPIC_SUB,
                                                            MQTT_USERNAME,
                                                            MQTT_PASSWORD)))
    
    # Move the gather outside the loop to wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())
    
