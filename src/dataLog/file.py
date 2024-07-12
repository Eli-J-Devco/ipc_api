# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import asyncio
import datetime
import json
import os
import sys
import base64
import gzip

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
value_many = []
value_dict = []
result_all = []

# Flag MQTT
flag_mqtt = False

count_mqtt = 0
countMonitor = 0

# Declare Variable 
first_call = True
status_device = ""     
msg_device = ""
status_register = ""
status_file = "Success"
data_mqtt = ""
sql_id_str = ""
device_name = ""
file_name = ""
data_in_file = ""
formatted_time1 = ""
time_interval = ""
time_create_file_insert_data_table_dev = ""

# Information Query
QUERY_TIME_SYNC_DATA=""
QUERY_ALL_DEVICES_SYNCDATA=""
QUERY_INSERT_SYNC_DATA=""
QUERY_INSERT_SYNC_DATA_EXECUTEMANY=""
QUERY_SELECT_COUNT_POINT_LIST=""
QUERY_SELECT_TOPIC = ""

# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# MQTT_TOPIC_SUB = Config.MQTT_TOPIC + "/Devices/#"
MQTT_TOPIC_SUB = ""
# MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/LogFile" 
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
def mqtt_public_paho_zip(host, port,topic, username, password, data_send):
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
                        data_value = str(field["value"]) if field["value"] is not None else ""
                        device_dict[device_id]["data"].append(data_value)
        
        # Convert dictionary to list
        result_list = list(device_dict.values())
    except Exception as err:
        print(f"process_message_result_list : '{err}'")
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
            # payload = json.loads(message.message.decode())
            payload = gzip_decompress(message.message)
            await process_message_result_list(payload)
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
async def create_filelog(base_path,id_device,head_file):
    # Query Global
    global QUERY_TIME_SYNC_DATA
    global QUERY_SELECT_COUNT_POINT_LIST
    global QUERY_INSERT_SYNC_DATA
    
    # Variable Global
    global status_device    
    global msg_device 
    global status_register
    global result_list
    global status_file
    global type_file
    global value_many
    global flag_mqtt
    global data_in_file
    global file_name
    global formatted_time1
    global countMonitor 
    
    # Get information from SQL
    id_device_fr_sys = id_device[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    
    # Take time to create file 
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    current_time = get_utc()
    current_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
    year,month, day = current_datetime.year , current_datetime.month,current_datetime.day
    
    # Declare Variable
    time_online = current_time
    data_insert =""
    data_to_write =""
    #-----------------------------------------------------
        
    for item in time_sync_data:
        type_file = item["type_protocol"]
        
    for item in result_all:
        sql_id = item["id"]
        # File creation time 
        modbus_device = [item['rtu_bus_address'] for item in result_all if item['id'] == sql_id][0]
        array_count_point = MySQL_Select(QUERY_SELECT_COUNT_POINT_LIST,(sql_id,))
        count = array_count_point[0]['COUNT(*)']
        DictID = [item for item in result_list if item["id"] == sql_id]
        
        print("result_list",result_list)
        
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
            file_name = f'{head_file}-{sql_id:03d}.{formatted_time1}.log'
            file_path = os.path.join(date_folder_path, file_name)
            source_file = date_folder_path + "/" + file_name
        
            if not data_to_write:
                data_in_file = ["" for i in range(count)]
            else:
                data_in_file = [str(val) for val in data_to_write]
                
            with open(file_path, 'w') as file:
                formatted_time2 = "'" + time_file + "'"
                file.write(f'{formatted_time2},0,0,0,{",".join(data_in_file)}')
                if countMonitor < 2 :
                    countMonitor += 1 
                else :
                    pass
                # code write data in table sync data ------------------------------------------------------------------
                time_insert = get_utc()
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
                #----------------------------------------------------------------- 
        except Exception as e:
            status_file = "Fault"
            print(f"Error during file creation is : {e}")
# Describe monitoring_device_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def monitoring_device_AllDevice(id_device,head_file,host, port,topic, username, password):
    global QUERY_ALL_DEVICES_SYNCDATA
    global QUERY_SELECT_TOPIC 
    result_topic = ""
    
    id_device_fr_sys = id_device[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (id_device_fr_sys,))
    
    result_topic = await MySQL_Select_v1 (QUERY_SELECT_TOPIC)
    topic = result_topic[0]["serial_number"]
    topic = topic + "/LogFile" 
    
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = monitoring_device(sql_id,id_device,head_file,host, port,topic, username, password)
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
    global countMonitor
    
    sql_id_str = ""
    device_name = ""
    
    current_time = get_utc()
    data = []
    time_online = current_time

    id_device_fr_sys = id_device[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (id_device_fr_sys,))
    
    id_device_fr_sys = id_device[1]
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    
    for item in time_sync_data:
        type_file = item["type_protocol"]
    
    if sql_id :
        file_name = f'{head_file}-{sql_id:03d}.{formatted_time1}.txt'
        DictID = [item for item in result_list if item["id"] == sql_id]
        if DictID:
            time_online = DictID[0]["time"]
            data = DictID[0]["data"]  
        try: 
            if formatted_time1 :
                data_mqtt={
                    "id_device":sql_id,
                    "status_data":status_device,
                    "status_chanel":status_file,
                    "file_name":file_name,
                    "time_stamp" :current_time,
                    "time_online" :time_online,
                    "time_log": time_interval,
                    "data_log":data,
                    }
            else :
                status_file = "fault"
                data_mqtt={
                    "id_device":sql_id,
                    "status_data":"old",
                    "status_chanel":"no_files_yet",
                    "file_name":"No files yet",
                    "time_stamp" :current_time,
                    "time_online" :time_online,
                    "time_log": time_interval,
                    "data_log":"No files yet",
                    }

            # File creation time 
            sql_id_str = str(sql_id)
            device_name = [item['name'] for item in result_all if item['id'] == sql_id][0] 
            mqtt_public_paho_zip(host,
                    port,
                    topic + f"/Channel{id_device_fr_sys}|{type_file}/"+sql_id_str+"|"+device_name,
                    username,
                    password,
                    data_mqtt)
        except Exception as err:
            print('Error monitoring_device : ',err)
    else:
        pass
        
#--------------------------------------------------------------------
# /**
# 	 * @description Insert data to Database
# 	 * @author bnguyen
# 	 * @since 04-01-2024
# 	 * @param {}
# 	 * @return  
# 	 */ 
async def insert_sync(id_device):
    # Variable Global
    global QUERY_INSERT_SYNC_DATA_EXECUTEMANY
    global value_many
    global status_file 
    id_device_fr_sys = id_device[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    # File creation time 
    
    if len(result_all) == len(value_many):
        MySQL_Insert_v4(QUERY_INSERT_SYNC_DATA_EXECUTEMANY,value_many)
    else :
        pass
# /**
# 	 * @description Insert data to Database
# 	 * @author bnguyen
# 	 * @since 04-01-2024
# 	 * @param {}
# 	 * @return  
# 	 */ 
async def delete_data_when_sync():
    try:
        # Delete rows from project_setup table where synced = 1
        query = "DELETE FROM sync_data WHERE synced = 1;"
        result_delete = MySQL_Delete(query)
        print(f"Deleted {result_delete.rowcount} rows from sync_data table")
    except Exception as err:
        print(f"Error MQTT subscribe delete_data_when_sync: '{err}'")
        
async def main():
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    # Query global 
    global QUERY_ALL_DEVICES_SYNCDATA
    global QUERY_TIME_CREATE_FILE
    global QUERY_TIME_SYNC_DATA
    global QUERY_INSERT_SYNC_DATA
    global QUERY_INSERT_SYNC_DATA_EXECUTEMANY
    global QUERY_SELECT_COUNT_POINT_LIST
    global QUERY_SELECT_TOPIC
    
    global MQTT_BROKER
    global MQTT_PORT
    global MQTT_TOPIC_SUB
    global MQTT_USERNAME
    global MQTT_PASSWORD

    # Variable global
    global time_interval
    
    topic = ""
    result_all = []
    result_topic = []
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_ALL_DEVICES_SYNCDATA = result_mybatis["QUERY_ALL_DEVICES_SYNCDATA"]
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_TIME_SYNC_DATA=result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_INSERT_SYNC_DATA_EXECUTEMANY=result_mybatis["QUERY_INSERT_SYNC_DATA_EXECUTEMANY"]
        QUERY_INSERT_SYNC_DATA=result_mybatis["QUERY_INSERT_SYNC_DATA"]
        QUERY_SELECT_COUNT_POINT_LIST=result_mybatis["QUERY_SELECT_COUNT_POINT_LIST"]
        QUERY_SELECT_TOPIC=result_mybatis["QUERY_SELECT_TOPIC"]
        
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_TIME_CREATE_FILE or not QUERY_ALL_DEVICES_SYNCDATA or not QUERY_TIME_SYNC_DATA or not QUERY_INSERT_SYNC_DATA or not QUERY_SELECT_COUNT_POINT_LIST or not QUERY_INSERT_SYNC_DATA_EXECUTEMANY or not QUERY_SELECT_TOPIC:
        print("Error not found data in file mybatis")
        return -1
    if len(arr) > 1 :
        result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(arr[1],))
        time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    else:
        pass
    
    result_topic = await MySQL_Select_v1(QUERY_SELECT_TOPIC)
    if result_topic != None :
        topic = result_topic[0]["serial_number"]
        MQTT_TOPIC_SUB = str(topic) + "/Devices/#"
        
        if not result_all :
            print("None of the devices have been selected in the database (check table upload_channel_device_map , divice_list)")
            return -1
        if not time_create_file_insert_data_table_dev :
            print("Unable to select synchronization time for data in the database.")
            return -1
        
        item = time_create_file_insert_data_table_dev[0]
        time_interval = item["time_log_interval"]
        position = time_interval.rfind("minute")
        number = time_interval[:position]
        int_number = int(number)

        #-------------------------------------------------------
        scheduler = AsyncIOScheduler()
        scheduler.add_job(create_filelog, 'cron',  minute = f'*/{int_number}', args=[FOLDER_PATH,
                                                                                    arr,
                                                                                    HEAD_FILE_LOG,
                                                                                    ])
        scheduler.add_job(monitoring_device_AllDevice, 'cron',  second = f'*/13' , args=[arr,
                                                                                HEAD_FILE_LOG,
                                                                                MQTT_BROKER,
                                                                                MQTT_PORT,
                                                                                MQTT_TOPIC_PUB,
                                                                                MQTT_USERNAME,
                                                                                MQTT_PASSWORD])
        scheduler.add_job(insert_sync, 'cron',  minute = f'*/{int_number}', second=1, args=[arr])
        scheduler.add_job(delete_data_when_sync, 'interval', hours=1, args=[])
        scheduler.start()
        #-------------------------------------------------------
        tasks = []
        tasks.append(asyncio.create_task(sub_mqtt(MQTT_BROKER,
                                                MQTT_PORT,
                                                MQTT_USERNAME,
                                                MQTT_PASSWORD,
                                                topic
                                                )))
        
        # Move the gather outside the loop to wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        pass
if __name__ == "__main__":
    asyncio.run(main())