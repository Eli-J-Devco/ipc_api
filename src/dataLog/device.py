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
from concurrent.futures import ThreadPoolExecutor

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

# Use passing parameters to file
# arr = sys.argv
# print(f'arr: {arr}')
# ------------------------------------

# Declare Variable 
result_list = []
result_all = []
status_device = ""     
msg_device = ""
status_register = ""
status_file = "Success"
status = "Waiting for the record to finish"
time_interval = ""

# Information Query
QUERY_TIME_CREATE_FILE = ""
QUERY_ALL_DEVICES = ""
QUERY_TIME_SYNC_DATA = ""
QUERY_SELECT_NAME_DEVICE = ""
    
# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC_SUB = Config.MQTT_TOPIC + "/Dev/#"
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/LogDevice" 
MQTT_USERNAME = Config.MQTT_USERNAME 
MQTT_PASSWORD = Config.MQTT_PASSWORD

# Information DB
DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_USERNAME = Config.DATABASE_USERNAME
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME

# Information Folder
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
    try:
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+file_name)
        statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
        result={}
        for item,value in enumerate(statement):
            for key in value.keys():
                result[key]=value[key]   

        return result  
    except Exception as e:
        print('An exception occurred:',e)
        return -1 
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
        print('Error not find object mybatis', err)
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
# ----- MQTT -----
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
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
                    if item['Config'] != 'MPPT':
                        value = str(item["Value"])
                        point_id = str(item["ItemID"])
                                    
                        result_value.append(value)
                        result_point_id.append(point_id)
                                
                result_values_dict[device_id] = result_value, result_point_id
                result_list = [
                    {"id": int(device_id), "point_id": point_id, "data": values, "time": current_time}
                    for device_id, (values, point_id) in result_values_dict.items()
                ]
                for item in result_list:
                    item['data'] = [val if val != 'None' else '' for val in item['data']]
            else: 
                pass
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
        
# Describe Insert_TableDevice_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def Insert_TableDevice_AllDevice():
    global QUERY_ALL_DEVICES
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = Insert_TableDevice(sql_id)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
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
async def Insert_TableDevice(sql_id):
    global result_list
    global status
    global QUERY_SELECT_NAME_DEVICE
    sql_queries = {}
    data = []
    result_all = []
    filedtable = []

    result_all = MySQL_Select(QUERY_SELECT_NAME_DEVICE, (sql_id,))
    
    for item in result_all:
            if item['namekey'] != 'MPPT':
                filedtable.append(item['id_pointkey'])
        
    DictID = [item for item in result_list if item["id"] == sql_id]
    
    if DictID:
        data = DictID[0]["data"]
    if not data:  # Check data if data empty 
        data = [None] * len(filedtable)
        
    try:
        # Write data to corresponding devices in the database
        time_insert_dev = get_utc()
        value_insert = (time_insert_dev, sql_id) + tuple(data)
        
        # Replace '0.0' with '' in the data tuple
        value_insert = tuple("0.0" if x == "" else x for x in value_insert)
        
        # Create Query
        columns = ["time", "id_device"]
        
        for itemp in filedtable:
            columns.append(itemp)
        
        table_name = f"dev_{sql_id}"

        # Create a query with REPLACE INTO syntax
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        val = value_insert

        # Check if the SQL query exists in the dictionary
        if sql_id in sql_queries:
            # Update the SQL query
            sql_queries[sql_id][0] = query
            sql_queries[sql_id][1] = val
        else:
            # Add a new entry to the dictionary
            sql_queries[sql_id] = [query, val]
        if query and val :
            MySQL_Insert_v3(sql_queries)
            status = "Data inserted successfully"
        else :
            status = "Waiting for the record to finish"
    except Exception as e:
        
        print(f"Error during file creation is : {e}")
                
# Describe monitoring_device_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def monitoring_device_AllDevice(host, port,topic, username, password):
    global QUERY_ALL_DEVICES
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = monitoring_device(sql_id,host, port,topic, username, password)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(sql_id,host, port,topic, username, password):
    
    global QUERY_ALL_DEVICES
    global QUERY_TIME_SYNC_DATA
    
    global status_device 
    global status_file
    global result_list
    global status 
    global time_interval
    
    current_time = get_utc()
    result_all = []
    data = []
    sql_id_str = ""
    device_name = ""
    

    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    DictID = [item for item in result_list if item["id"] == sql_id]
    if DictID:
        data = DictID[0]["data"]
                
    try:
        data_mqtt={
            "ID_DEVICE":sql_id,
            "STATUS_CHANNEL":status,
            "TIME_STAMP" :current_time,
            "TIME_LOG": time_interval ,
            "DATA_LOG":data,
            }
        
        # File creation time 
        sql_id_str = str(sql_id)
        device_name = [item['name'] for item in result_all if item['id'] == sql_id][0] 
        
        push_data_to_mqtt(host,
                port,
                topic + f"/"+sql_id_str+"|"+device_name,
                username,
                password,
                data_mqtt)
    except Exception as err:
        print('Error monitoring_device : ',err)
        
async def main():
    
    global QUERY_TIME_CREATE_FILE
    global QUERY_ALL_DEVICES 
    global QUERY_TIME_SYNC_DATA
    global QUERY_SELECT_NAME_DEVICE
    
    global time_interval
    
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TIME_SYNC_DATA = result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_SELECT_NAME_DEVICE = result_mybatis["QUERY_SELECT_NAME_DEVICE"]
    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_TIME_CREATE_FILE or not QUERY_ALL_DEVICES  or not QUERY_TIME_SYNC_DATA or not QUERY_SELECT_NAME_DEVICE:
        print("Error not found data in file mybatis") 
        return -1
    #------------------------------------------------------------------------
    time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    
    item = time_create_file_insert_data_table_dev[0]
    time_interval = item["time_log_interval"]
    position = time_interval.rfind("minute")
    number = time_interval[:position]
    int_number = int(number)
    
    if not time_create_file_insert_data_table_dev or not result_all:
        print("Error not found data in Database")
        return -1
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(Insert_TableDevice_AllDevice, 'cron', minute = f'*/{int_number}')
    scheduler.add_job(monitoring_device_AllDevice, 'cron',  second = f'*/10' , args=[MQTT_BROKER,
                                                                            MQTT_PORT,
                                                                            MQTT_TOPIC_PUB,
                                                                            MQTT_USERNAME,
                                                                            MQTT_PASSWORD])
    scheduler.start()
    
    tasks = []
    tasks.append(Get_MQTT(MQTT_BROKER,
                                    MQTT_PORT,
                                    MQTT_TOPIC_SUB,
                                    MQTT_USERNAME,
                                    MQTT_PASSWORD
                                    ))
    
    await asyncio.gather(*tasks, return_exceptions=False)
    #-------------------------------------
    await asyncio.sleep(0.05)
if __name__ == "__main__":
    asyncio.run(main())


