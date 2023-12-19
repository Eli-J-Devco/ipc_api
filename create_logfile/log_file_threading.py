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

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config import *
from libMySQL import *

# Use passing parameters to file
arr = sys.argv
# print(f'arr: {arr}')
# ------------------------------------
result_list =[]
status_device =""     
msg_device =""
status_register =""
status_file ="Success"

# Variables 
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC_SUB = Config.MQTT_TOPIC + "/Dev/#"
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/Log" 
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
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    print(path+file_name)
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
# 	 * @description check query in mybatis
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {data,item,object_name}
# 	 * @return {}
# 	 */
def func_check_data_mybatis(data,item,object_name):
    try:
        
        if data[item].get(object_name):
            return data[item].get(object_name)
        else:
            return ""
        
    except Exception as err:
        print('Error not find object mybatis')
    return 
#----------------------------------------
# /**
# 	 * @description take time 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {}
# 	 * @return datetime
# 	 */
def get_utc():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
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
async def get_data_from_MQTT(host, port, topic, username, password):
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
        await client.start()
        await client.subscribe(topic)
        while True:
            current_time = get_utc()
            message = await client.messages.get()
            if message is None:
                time.sleep(5)
            # cut string get device id value from sud mqtt
            cut_topic1 = message.topic[8:]
            device_id = cut_topic1.split("|")[0]
            if status_file == "Success" :
                result_value = []
                result_point_id = []
            else :
                result_value == result_values_dict
                
            mqtt_result = json.loads(message.message.decode())
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
async def create_and_write_data_to_file(sql_id,base_path,id_device,head_file,host, port, topic, username, password):
    
    id_device_fr_sys = id_device[1]
    result_mybatis=get_mybatis('/mybatis/logfile.xml')
    QUERY_TIME_SYNC_DATA=result_mybatis["QUERY_TIME_SYNC_DATA"]
    QUERY_ALL_DEVICES=result_mybatis["QUERY_ALL_DEVICES"]
    QUERY_INSERT_SYNC_DATA=result_mybatis["QUERY_INSERT_SYNC_DATA"]
    QUERY_SELECT_COUNT_POINT_LIST=result_mybatis["QUERY_SELECT_COUNT_POINT_LIST"]
    QUERY_TIME_CREATE_FILE=result_mybatis["QUERY_TIME_CREATE_FILE"]
    
    if QUERY_TIME_SYNC_DATA != -1 and QUERY_ALL_DEVICES  != -1 and QUERY_INSERT_SYNC_DATA  != -1 and QUERY_SELECT_COUNT_POINT_LIST  != -1 and QUERY_TIME_CREATE_FILE  != -1 :
        pass
    else:           
        print("Error not found data in file mybatis")
        return -1
    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    array_count_point = MySQL_Select(QUERY_SELECT_COUNT_POINT_LIST,(id_device_fr_sys,))
    count = array_count_point[0]['COUNT(*)']
    #---------------------------------------------------------------------------------------------------------------
    while True:
        current_time = get_utc()
        current_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        year,month, day, hour, minute, second = current_datetime.year , current_datetime.month,current_datetime.day,current_datetime.hour, current_datetime.minute, current_datetime.second
        global status_device    
        global msg_device 
        global status_register
        global result_list
        global status_file
        global type_file
        data_to_write =""
        data_in_file = ""
        time_online = current_time
        #-----------------------------------------------------
        for item in time_create_file_insert_data_table_dev:
            time = item["time_log_interval"]
            position = time.rfind("minute")
            number = time[:position]
            int_number = int(number)
            
        for item in time_sync_data:
            type_file = item["type_protocol"]
        
        # File creation time 
            if minute % int_number == 0 and second % 10 == 0:
                    sql_id_str = str(sql_id)
                    device_name = [item['name'] for item in result_all if item['id'] == sql_id][0]
                    modbus_device = [item['rtu_bus_address'] for item in result_all if item['id'] == sql_id][0]
                    
                    DictID = [item for item in result_list if item["id"] == sql_id]
                    
                    for item in DictID:
                        data = item["data"]
                        data_to_write = data
                        
                    for item in DictID:
                        time_online = item["time"]
                        
                    date_folder_path = os.path.join(base_path, f"{id_device_fr_sys}\\{type_file}\\{sql_id}\\{year}\\{month}\\{day}")
                    try:
                        os.makedirs(date_folder_path, exist_ok=True)
                        time_file = get_utc()
                        time_file_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                        formatted_time1 = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
                        file_name = f'{head_file}-{sql_id:03d}.{formatted_time1}.txt'
                        file_path = os.path.join(date_folder_path, file_name)
                        source_file = date_folder_path + "\\" + file_name
                        
                        if not data_to_write:
                            data_in_file = ["" for i in range(count)]
                        else:
                            data_in_file = [str(val) for val in data_to_write]

                        with open(file_path, 'w') as file:
                            formatted_time2 = "'" + time_file + "'"
                            file.write(f'{formatted_time2},0,0,0,{",".join(data_in_file)}')
                            
                            # code write data in table sync data ------------------------------------------------------------------
                            time_insert = get_utc()
                            values = (time_insert, sql_id, modbus_device, date_folder_path, source_file, file_name, time_insert, 
                                    f'{formatted_time2},0,0,0,{",".join(data_in_file)}', id_device_fr_sys,modbus_device, date_folder_path, 
                                    source_file, type_file, current_time, f'{formatted_time2},0,0,0,{",".join(data_in_file)}', id_device_fr_sys)
                            MySQL_Insert_v1(QUERY_INSERT_SYNC_DATA,values)
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
            await asyncio.sleep(1)
    
async def main():
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]

    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    print("----------------------------", result_all)
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        print(sql_id)
        tasks.append(asyncio.create_task(create_and_write_data_to_file(sql_id,
                                                                        FOLDER_PATH,
                                                                        arr,
                                                                        HEAD_FILE_LOG,
                                                                        MQTT_BROKER,
                                                                        MQTT_PORT,
                                                                        MQTT_TOPIC_PUB,
                                                                        MQTT_USERNAME,
                                                                        MQTT_PASSWORD)))
        tasks.append(asyncio.create_task(get_data_from_MQTT(MQTT_BROKER,
                                                                MQTT_PORT,
                                                                MQTT_TOPIC_SUB,
                                                                MQTT_USERNAME,
                                                                MQTT_PASSWORD)))

    # Move the gather outside the loop to wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())