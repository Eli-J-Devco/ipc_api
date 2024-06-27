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
result_list_MPPT = []
result_list_MPPTSTRING = []
status_device = ""   
code_error = 0
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
QUERY_SELECT_TOPIC = ""
    
# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# MQTT_TOPIC_SUB = Config.MQTT_TOPIC + "/Devices/#"
MQTT_TOPIC_SUB = ""
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/LogDevice" 
MQTT_TOPIC_PUB = ""
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
# Describe process_message_result_list 
# 	 * @description process_message_result_list
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param { message}
# 	 * @return result_list
# 	 */ 
async def process_message_result_list(message):
    global status_device    
    global msg_device 
    global status_register
    global result_list
    global status_file

    device_dict = {}
    
    try:
        current_time = get_utc()
        # create list data device from topic ALL devices 
        for items in message:
            device_id = items["id_device"]
            status_device = items["status_device"]
            message = items["message"]
            status_register = items["status_register"]
            fields = items["fields"]
            type_device_type = items["type_device_type"]
            
            if device_id not in device_dict:
                device_dict[device_id] = {
                    "id": int(device_id),
                    "point_id": [],
                    "data": [],
                    "time": current_time,
                    "status_device": status_device,
                    "msg_device": msg_device,
                    "status_register": status_register
                }
            
            # Condition log device 
            if type_device_type != 1:      
                for field in fields:
                    if field['config'] != 'MPPT':
                        device_dict[device_id]["point_id"].append(str(field["id"]))
                        data_value = str(field["value"]) if field["value"] is not None else 0.0
                        device_dict[device_id]["data"].append(data_value)
        
        # Convert dictionary to list
        result_list = list(device_dict.values())
    except Exception as err:
        print(f"process_message_result_list : '{err}'")
# Describe process_message_result_list_mptt 
# 	 * @description process_message_result_list_mptt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param { message}
# 	 * @return result_list_MPPT
# 	 */ 
async def process_message_result_list_mptt(message):
    global status_device    
    global msg_device 
    global status_register
    global status_file
    global result_list_MPPT 

    device_id = 0 
    type_device_type = 0
    name_device_type = ""
    mppt_dict = {}

    try:
        # create list data device from topic ALL devices 
        for items in message:
            device_id = items["id_device"]
            fields = items["fields"]
            name_device_type = items["name_device_type"]
            type_device_type = items["type_device_type"]
            # Condition log device 
            if type_device_type != 1 and name_device_type == "PV System Inverter":      
                for field in fields:
                    if field['config'] == 'MPPT':
                        # Get data for table mppt 
                        MPPTVolt = field['value']['mppt_volt']
                        MPPTAmps = field['value']["mppt_amps"]
                        MPPTpoint_key_strings = field['value']["mppt_string"]
                        MPPTpoint_key = field['point_key']
                        for item_string in MPPTpoint_key_strings:
                            MPPTpoint_key_string = item_string['point_key']
                        
                        key_mppt = (int(device_id), MPPTpoint_key, MPPTpoint_key_string)
                        if key_mppt in mppt_dict:
                            # If the object already exists, update the values
                            mppt_dict[key_mppt]['MPPTVolt'] = MPPTVolt
                            mppt_dict[key_mppt]['MPPTAmps'] = MPPTAmps
                        else:
                            # If it does not exist, add a new object to the dictionary
                            mppt_dict[key_mppt] = {
                                "id": int(device_id),
                                "point_key": MPPTpoint_key,
                                "point_key_string": MPPTpoint_key_string,
                                "MPPTVolt": MPPTVolt,
                                "MPPTAmps": MPPTAmps
                            }
                        
                        # Pass the values ​​from the dictionary into result_list_MPPT
                        result_list_MPPT = list(mppt_dict.values())
    except Exception as err:
        print(f"process_message_result_list_mptt_list: '{err}'")
        
# Describe handle_messages_driver 
# 	 * @description handle_messages_driver
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {client}
# 	 * @return all topic , all message
# 	 */ 
async def handle_messages_driver(client):
    while True:
        try:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            payload = json.loads(message.message.decode())
            await process_message_result_list(payload)
            await process_message_result_list_mptt(payload)
        except Exception as err:
            print(f"Error handle_messages_driver: '{err}'")
# Describe sub_mqtt 
# 	 * @description sub_mqtt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def sub_mqtt(host, port, username, password, serial_number_project):
    topics = [serial_number_project + "/Devices/All"]
    try:
        client = mqttools.Client(
            host=host,
            port=port,
            username=username,
            password=bytes(password, 'utf-8'),
            subscriptions=topics,
            connect_delays=[1, 2, 4, 8]
        )
        while True:
            await client.start()
            await handle_messages_driver(client)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT sub_mqtt: '{err}'")
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
        task = Insert_TableDevice(sql_id,result_all)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
# --------------------------------------------------------------------
# /**
# 	 * @description 
#       - create and write data in file  
#       - sync data file with database 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port, topic, username, password}
# 	 * @return result_list 
# 	 */ 
async def Insert_TableDevice(sql_id,result_all):
    global result_list
    global status
    global status_device 
    global status_register
    global code_error
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
        status_device = DictID[0]["status_device"]
        status_register = DictID[0]["status_register"]
        
    if not data:  # Check data if data empty 
        data = [None] * len(filedtable)

    if status_device == "offline" :
        code_error = 139
    elif status_device == "online" :
        if len(status_register) > 0 :
            code_error = status_register[0]["ERROR_CODE"]
        else :
            code_error = 0
    else :
        pass

    try:
        # Write data to corresponding devices in the database
        time_insert_dev = get_utc()
        value_insert = (time_insert_dev, sql_id , code_error) + tuple(data)
        
        # Replace '0.0' with '' in the data tuple
        value_insert = tuple("0.0" if x == "" else x for x in value_insert)
        
        # Create Query
        columns = ["time", "id_device", "error"]
        
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
            # print("sql_queries",sql_queries)
            MySQL_Insert_v3(sql_queries)
            status = "Data inserted successfully"
        else :
            status = "Waiting for the record to finish"
    except Exception as e:
        
        print(f"Error during file creation is : {e}")

# async def Insert_TableDevice_AllDevice():
#     global QUERY_ALL_DEVICES
#     result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
#     sql_queries = {}
#     values = []
#     for item in result_all:
#         sql_id = item["id"]
#         print("sql_id", sql_id)
#         query, value = await Insert_TableDevice(sql_id, result_all)
#         if query and value:
#             if sql_id in sql_queries:
#                 sql_queries[sql_id][0].append(query)
#                 sql_queries[sql_id][1].append(value)
#             else:
#                 sql_queries[sql_id] = [[query], [value]]
#     for key, value in sql_queries.items():
#         try:
#             await MySQL_Insert_v3(value[0], value[1])
#             status = "Data inserted successfully"
#         except Exception as e:
#             print(f"Error inserting data for device {key}: {e}")
#             status = "Error inserting data"

# async def Insert_TableDevice(sql_id, result_all):
#     global QUERY_SELECT_NAME_DEVICE
#     result_device = MySQL_Select(QUERY_SELECT_NAME_DEVICE, (sql_id,))
#     filedtable = []
#     for item in result_device:
#         if item['namekey'] != 'MPPT':
#             filedtable.append(item['id_pointkey'])
    
#     data = [None] * len(filedtable)
#     status_device = "offline"
#     status_register = []
#     code_error = 139

#     try:
#         time_insert_dev = get_utc()
#         value_insert = (time_insert_dev, sql_id, code_error) + tuple(data)
#         value_insert = tuple("0.0" if x == "" else x for x in value_insert)
#         columns = ["time", "id_device", "error"] + filedtable
#         table_name = f"dev_{sql_id}"
#         query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
#         return query, value_insert
#     except Exception as e:
#         print(f"Error during file creation is : {e}")
#         return None, None

# async def MySQL_Insert_v3(queries, values):
#     for query, value in zip(queries, values):
#         try:
#             await MySQL_Execute_v1(query, value)
#         except Exception as e:
#             print(f"Error inserting data: {e}")
# /**
# 	 * @description 
#       - create and write data in file  
#       - sync data file with database 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port, topic, username, password}
# 	 * @return result_list 
# 	 */ 
async def Insert_TableMPPT():
    global result_list_MPPT
    val_list_MPPT = []
    val_list_STRING = []
    id_device = ""
    MPPTKey = ""
    MPPTKey_string = ""
    voltage = ""
    current = ""
    print("result_list_MPPT",result_list_MPPT)
    try:
        if result_list_MPPT :
            for item in result_list_MPPT:
                if 'id' in item and 'point_key' in item and 'point_key_string' in item and 'MPPTVolt' in item and 'MPPTAmps' in item:
                    id_device = item['id']
                    MPPTKey = item['point_key']
                    MPPTKey_string = item['point_key_string']
                    voltage = item['MPPTVolt']
                    current = item['MPPTAmps']

                    val_list_MPPT.append((voltage, current, id_device, MPPTKey))
                    val_list_STRING.append((current, id_device, MPPTKey_string))

            query = "UPDATE device_mppt SET voltage = %s, current = %s WHERE id_device_list = %s AND namekey = %s;"
            MySQL_Insert_v4(query, val_list_MPPT)
            query = "UPDATE device_mppt_string SET current = %s WHERE id_device_mppt = %s AND namekey = %s;"
            MySQL_Insert_v4(query, val_list_STRING)
            
            result_list_MPPT = []
        else:
            pass
    except Exception as e:
        print(f"Error during data insertion: {e}")
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
    global QUERY_SELECT_TOPIC 
    result_topic = "" 
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    
    result_topic = await MySQL_Select_v1 (QUERY_SELECT_TOPIC)
    topic = result_topic[0]["serial_number"]
    topic = topic + "/LogDevice"  
    
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
    
    current_time = ""
    result_all = []
    data = []
    sql_id_str = ""
    device_name = ""
    
    current_time = get_utc()
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    DictID = [item for item in result_list if item["id"] == sql_id]
    if DictID:
        data = DictID[0]["data"]
                
    try:
        data_mqtt={
            "id_device":sql_id,
            "status_chanel":status,
            "time_stamp" :current_time,
            "time_log": time_interval ,
            "data_log":data,
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
    global QUERY_SELECT_TOPIC
    
    global MQTT_BROKER
    global MQTT_PORT
    global MQTT_TOPIC_SUB
    global MQTT_USERNAME
    global MQTT_PASSWORD
    
    global time_interval
    topic = ""
    result_all = []
    result_topic = []
    
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TIME_SYNC_DATA = result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_SELECT_NAME_DEVICE = result_mybatis["QUERY_SELECT_NAME_DEVICE"]
        QUERY_SELECT_TOPIC = result_mybatis["QUERY_SELECT_TOPIC"]
        
    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_TIME_CREATE_FILE or not QUERY_ALL_DEVICES  or not QUERY_TIME_SYNC_DATA or not QUERY_SELECT_NAME_DEVICE or not QUERY_SELECT_TOPIC:
        print("Error not found data in file mybatis") 
        return -1
    #------------------------------------------------------------------------
    time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    
    result_topic = await MySQL_Select_v1(QUERY_SELECT_TOPIC)
    if result_topic != None :
        topic = result_topic[0]["serial_number"]
        MQTT_TOPIC_SUB = str(topic) + "/Devices/#"
        
        item = time_create_file_insert_data_table_dev[0]
        time_interval = item["time_log_interval"]
        position = time_interval.rfind("minute")
        number = time_interval[:position]
        int_number = int(number)

        if not result_all :
            print("None of the devices have been selected in the database")
            return -1
        if not time_create_file_insert_data_table_dev :
            print("Unable to select synchronization time for data in the database.")
            return -1
        
        
        scheduler = AsyncIOScheduler()
        scheduler.add_job(Insert_TableDevice_AllDevice, 'cron', minute = f'*/{int_number}')
        scheduler.add_job(Insert_TableMPPT, 'cron', minute = f'*/{int_number}')
        scheduler.add_job(monitoring_device_AllDevice, 'cron',  second = f'*/10' , args=[MQTT_BROKER,
                                                                                MQTT_PORT,
                                                                                MQTT_TOPIC_PUB,
                                                                                MQTT_USERNAME,
                                                                                MQTT_PASSWORD])
        scheduler.start()
        
        tasks = []
        # tasks.append(Get_MQTT(MQTT_BROKER,
        #                                 MQTT_PORT,
        #                                 MQTT_TOPIC_SUB,
        #                                 MQTT_USERNAME,
        #                                 MQTT_PASSWORD
        #                                 ))
        tasks.append(sub_mqtt(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            topic,
                            ))
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        pass
    #-------------------------------------
    await asyncio.sleep(0.05)
if __name__ == "__main__":
    asyncio.run(main())


