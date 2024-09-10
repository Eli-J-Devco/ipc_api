import asyncio
import copy
import datetime
import ftplib
import json
import logging
import os
import subprocess
import sys
from functools import partial
import mqttools
import mybatis_mapper2sql
import paho.mqtt.publish as publish

sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
print(f'path: {path}')
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configs.config import Config
from utils.libMySQL import *
from utils.mqttManager import (gzip_decompress,
                               mqtt_public_common, mqtt_public_paho,
                               mqtt_public_paho_zip, mqttService)
# Information DB
arr = sys.argv
id_upload_chanel = arr
DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_USERNAME = Config.DATABASE_USERNAME
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
FTPSERVER_HOSTNAME = Config.FTPSERVER_HOSTNAME
FTPSERVER_PORT = Config.FTPSERVER_PORT
FTPSERVER_USERNAME = Config.FTPSERVER_USERNAME
FTPSERVER_PASSWORD = Config.FTPSERVER_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME
URL_SERVER_SYNC = Config.URL_SERVER_SYNC
URL_SERVER_SYNC_FILE = Config.URL_SERVER_SYNC_FILE 

# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/UpData" 
MQTT_TOPIC_PUB = ""
MQTT_TOPIC_SUB = "Control"
MQTT_USERNAME = Config.MQTT_USERNAME 
MQTT_PASSWORD = Config.MQTT_PASSWORD

# Information Query
QUERY_ALL_DEVICES_SYNCDATA = ""
QUERY_TIME_SYNC_DATA = ""
QUERY_SYNC_SERVER = ""
QUERY_UPDATE_DATABASE = ""
QUERY_GETDATA_SERVER = ""
QUERY_UPDATE_ERR_DATABASE = ""
QUERY_TIME_RETRY = ""
QUERY_UPDATE_NUMBERRETRY = ""
QUERY_NUMER_FILE = ""
QUERY_SYNC_MULTIFILE_SERVER = ""
QUERY_SYNC_ERROR_MQTT = ""
QUERY_SELECT_NAME_DEVICE = ""
QUERY_UPDATE_SERIAL_NUMBER = ""
QUERY_SELECT_SERIAL_NUMBER = ""
QUERY_SELECT_URL = ""
QUERY_SYNC_FILELOG_SERVER = ""
QUERY_TIME_CREATE_FILE = ""
QUERY_SELECT_TOPIC = ""

# Declare Variable 
data_sent_server_list = []
array_file = []
array_files = []
json_data_list = []
vals = []

json_data = {}
json_datas = {}
data_sent_server = {}

data = 0
status_sync = 0 
count = 0
sync_immediately = 0 
count_FTP_Server = 0
number_device = 10 
count = 0 
int_number = 0

flag_sync_immediately = False 
flag_end_update = False
flag_retry = False
multifile = False
isUploadSuccess = False

serial_number = ""
time_retry = ""
type_file = ""
time_sentdata = 0

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
        print(err)
        return None
# /**
# 	 * @description take time 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {}
# 	 * @return datetime
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
# 	 * @param {device.file_name}
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
# # Describe get serial number for system
# # /**
# # 	 * @description get_serial_number_windows
# # 	 * @author bnguyen
# # 	 * @since 27/2/2024
# # 	 * @param {}
# # 	 * @return serial number
# # 	 */  
# def get_serial_number_windows():
#     try:
#         if sys.platform == 'win32':
#             # Chạy lệnh wmic để lấy thông tin SerialNumber
#             result = subprocess.check_output(["wmic", "bios", "get", "serialnumber"]).decode("utf-8")
#             # Lọc kết quả để chỉ lấy SerialNumber
#             serial_number = result.strip().split("\n")[1]
#             return serial_number
#         else:
#             pass
#     except Exception as e:
#         print(f"Lỗi khi lấy thông tin SerialNumber: {e}")
#         return None
# ----- MQTT -----
# /**
# 	 * @description Sub data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return mqtt_result
# 	 */
async def subMQTT(host, port, topic, username, password):
    global sync_immediately 
    global flag_sync_immediately
    mqtt_result =""
    message =""
    global QUERY_TIME_SYNC_DATA 
    global id_upload_chanel 
    id_device_fr_sys = id_upload_chanel[1]
    
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]  
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client :
            print("Error connect with MQTT")
            return -1 

        await client.start()
        await client.subscribe(topic)
        while True:
            message = await client.messages.get()
            if not message :
                print("Not find message from MQTT")
                return -1 
        
            mqtt_result = json.loads(message.message.decode())
            sync_immediately = mqtt_result
            if sync_immediately == 0 :
                flag_sync_immediately = False
            
            if sync_immediately == 1 and flag_sync_immediately == False:
                if type_file == "URL" : 
                    await sync_ServerURL_Database(URL_SERVER_SYNC)
                if type_file == "FTP" : 
                    await sync_ServerFTP_Database(FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD)
            else :
                pass
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
    return mqtt_result
# Describe sync_ServerFile_Database_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def colectDatatoPushMQTT_AllDevice(host,port,topic,username,password):
    global id_upload_chanel
    global QUERY_ALL_DEVICES_SYNCDATA
    global QUERY_SELECT_TOPIC
    result_topic = ""
    id_device_fr_sys = id_upload_chanel[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (id_device_fr_sys,))
    
    result_topic = await MySQL_Select_v1 (QUERY_SELECT_TOPIC)
    topic = result_topic[0]["serial_number"]
    topic = topic + "/UpData" 

    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = colectDatatoPushMQTT(sql_id,host,port,topic,username,password)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 10/1/2024
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
async def colectDatatoPushMQTT(sql_id,host,port,topic,username,password):
    global QUERY_TIME_SYNC_DATA
    global QUERY_SYNC_SERVER
    global QUERY_ALL_DEVICES_SYNCDATA
    
    global id_upload_chanel
    global status_sync
    global multifile
    global number_device 
    global json_data
    global time_sentdata
    global int_number
    
    data_sent_server_mqtt = []
    data_sent_server_list_mqtt = []
    data_sync_server_mqtt = []
    data_sync_dict = []
    devices = []
    data_mqtts = []
    result1 =[]
    number_file = ""
    time_sync = ""

    id_device_fr_sys = id_upload_chanel[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]
    result1 = MySQL_Select(QUERY_NUMER_FILE,(id_device_fr_sys,))
    number_file = result1[0]["remaining_files"]
    
    class MyVariable1:
        def __init__(self, time_id, file_name, number_time_retry, id_device,id_device_str, device_name, error, result_error, status ):
            self.time_id = time_id
            self.file_name = file_name
            self.number_time_retry = number_time_retry
            self.id_device = id_device
            self.id_device_str = str(id_device)
            self.device_name = device_name
            self.error = error
            self.result_error = result_error
            self.status = status

    for _ in range(number_device):
        device = MyVariable1("", "", "", "", "", "", "", "", False)
        devices.append(device)
    if sql_id : 
        # Push When Sent data once file 
        if multifile is False :
                data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,sql_id,))
                if data_sync_server_mqtt :
                    data_sync_dict = data_sync_server_mqtt[0]
                    if 'id_device' not in data_sync_dict:
                        return -1 
                    if 'filename' not in data_sync_dict:
                        return -1 
                    if 'number_of_time_retry' not in data_sync_dict:
                        return -1 
                    
                    device.id_device = data_sync_dict['id_device']        
                    device.file_name = data_sync_dict['filename']
                    device.number_time_retry = data_sync_dict['number_of_time_retry']
                    device.result_error = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,device.file_name))
                    device.error = device.result_error[0]["error"]
                    # File creation time 
                    device.id_device_str = str(device.id_device)
                    device.device_name = [item['name'] for item in result_all if item['id'] == device.id_device][0]
                    
                    current_time = get_utc()
                    ts_timestamp = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
                    datetime_obj = datetime.datetime.fromtimestamp(ts_timestamp)
                    date_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
                    
                    if status_sync == 1 or isUploadSuccess == True: 
                        device.status = "Success"
                    else :
                        device.status = "Fault"
                    if int_number:
                        if 0 <= time_sentdata <= 24:
                            time_sync = str(int_number) +" "+ "hour"
                        elif time_sentdata == 95:
                            time_sync = "Connect Every 12 hours"
                        elif time_sentdata == 96:
                            time_sync = "Connect Every 8 hours"
                        elif time_sentdata == 97:
                            time_sync = "Connect Every " + str(int_number) + " minute"
                        elif time_sentdata == 98:
                            time_sync = "Connect Every 15 minutes"
                        elif time_sentdata == 99:
                            time_sync = "Connect Every Hour"
                    else :
                        pass
                        
                    data_mqtt={
                        "id_device":device.id_device,
                        "file_name": device.file_name,
                        "time_stamp": date_str,
                        "status_file_sever": device.status,
                        "time_sync": time_sync ,
                        "remainder_file":number_file,
                        "number_of_retry":device.number_time_retry,
                    }
                    mqtt_public_paho_zip(host,
                            port,
                            topic + f"/Channel{id_device_fr_sys}|{type_file}/" + device.id_device_str + "|" + device.device_name ,
                            username,
                            password,
                            data_mqtt)
        else :
            data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,sql_id,))
            if data_sync_server_mqtt :
                for item in data_sync_server_mqtt :
                    data_sync_dict = item       
                    id_device_temp = data_sync_dict['id_device']
                    filename_temp = data_sync_dict['filename']  
                    number_time_retry_temp = data_sync_dict['number_of_time_retry']
                    error_temp = data_sync_dict['error']
                    
                    data_sent_server_mqtt = { "id_device": id_device_temp , "filename": filename_temp,"number_of_time_retry": number_time_retry_temp , "error":error_temp}
                    data_sent_server_list_mqtt.append(data_sent_server_mqtt)
            if data_sent_server_list_mqtt and len(data_sent_server_list_mqtt) == number_device :
                for i in range (number_device):    
                    devices[i].id_device = data_sent_server_list_mqtt[i]['id_device']        
                    devices[i].file_name = data_sent_server_list_mqtt[i]['filename']
                    devices[i].number_time_retry = data_sent_server_list_mqtt[i]['number_of_time_retry']
                    devices[i].result_error = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,devices[i].file_name))
                    
                    # File creation time 
                    devices[i].id_device_str = str( devices[i].id_device)
                    devices[i].device_name = [item['name'] for item in result_all if item['id'] == devices[i].id_device][0]
                    
                    current_time = get_utc()
                    ts_timestamp = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
                    datetime_obj = datetime.datetime.fromtimestamp(ts_timestamp)
                    date_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")

                    if status_sync == 1 or isUploadSuccess == True: 
                        devices[i].status = "Success"
                    else :
                        devices[i].status = "Fault"
                    
                    if time_sentdata and int_number:
                        if 0 <= time_sentdata <= 24:
                            time_sync = str(time_sentdata) + "hour"
                        elif time_sentdata == 95:
                            time_sync = "Connect Every 12 hours"
                        elif time_sentdata == 96:
                            time_sync = "Connect Every 8 hours"
                        elif time_sentdata == 97:
                            time_sync = "Connect Every " + str(int_number) + " minute"
                        elif time_sentdata == 98:
                            time_sync = "Connect Every 15 minutes"
                        elif time_sentdata == 99:
                            time_sync = "Connect Every Hour"
                    else :
                        pass
                    
                    data_mqtt={
                        "id_device":devices[i].id_device,
                        "file_name": devices[i].file_name,
                        "time_stamp": date_str,
                        "status_file_sever": devices[i].status,
                        "time_sync": time_sync ,
                        "remainder_file":number_file,
                        "number_of_retry": devices[i].number_time_retry, 
                    }

                    data_mqtts.append(data_mqtt) 
                    
                    mqtt_public_paho_zip(host,
                            port,
                            topic + f"/Channel{id_device_fr_sys}|{type_file}/" + devices[i].id_device_str + "|" + devices[i].device_name ,
                            username,
                            password,
                            data_mqtts)
    else: 
        pass
# Describe sync_ServerFile_Database_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_ServerURL_Database_AllDevice():
    global id_upload_chanel
    global QUERY_ALL_DEVICES_SYNCDATA
    id_device_fr_sys = id_upload_chanel[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (id_device_fr_sys,))
    
    print("result================================" , result_all)
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = sync_ServerURL_Database(sql_id)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
# Describe sync_Server_Database
# /**
# 	 * @description read data from database , send data to server , update data sent in database
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_ServerURL_Database(id_device):
    
    # Step 1 : Read data from database 
    current_time = get_utc()
    
    global id_upload_chanel
    global data_sent_server
    global status_sync
    global count
    global multifile
    global time_retry
    global vals
    global json_data 
    global number_device
    global array_file
    
    global QUERY_SYNC_SERVER
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_DATABASE
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    global QUERY_SELECT_NAME_DEVICE
    global QUERY_SELECT_SERIAL_NUMBER
    global QUERY_SELECT_URL
    global QUERY_TIME_SYNC_DATA
    global QUERY_ALL_DEVICES_SYNCDATA
    
    id_device_fr_sys = id_upload_chanel[1]
    data_sync_server = []
    template_names  = []
    data_sent_server_list = []
    data_sync_dict = []
    devices = []
    file = []
    files = []
    data_insert_many_temp = []
    data_insert_many = []
    val = []
    result =[]
    result1 =[]
    result2 =[]
    result3 =[]
    
    file = {}
    
    name_serial_device = ""
    url = ""
    response =""
    number_file =""
    json_data_total = ""

    class MyVariable2:
        def __init__(self, time_id, id_device, modbusdevice, source, ensuredir, file_name, file_content, file_size, datasql, data_file):
            self.time_id = time_id
            self.id_device = id_device
            self.modbusdevice = modbusdevice
            self.source = source
            self.ensuredir = ensuredir
            self.file_name = file_name
            self.file_content = file_content
            self.file_size = file_size
            self.datasql = datasql
            self.data_file = data_file

    for _ in range(number_device):
        device = MyVariable2("", "", "", "", "","", "", 0 , "", "")
        devices.append(device)
    
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]
    
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    
    result1 = MySQL_Select(QUERY_NUMER_FILE,(id_device_fr_sys,))
    number_file = result1[0]["remaining_files"]
    
    if number_file <= len(result_all) :
        multifile = False 
    else :
        multifile = True 
    
    result2 = await MySQL_Select_v1(QUERY_SELECT_SERIAL_NUMBER)
    name_serial_device = result2[0]["serial_number"] 
    
    result3 = MySQL_Select(QUERY_SELECT_URL,(id_device_fr_sys,))
    url = result3[0]["uploadurl"] 
    
    if number_file != 0 and url:
        if multifile is False :
            if count == 0 :
                try :
                    data_sync_server = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,id_device,))
                    if data_sync_server :
                        data_sync_dict = data_sync_server[0]
                        if 'id' not in data_sync_dict:
                            return -1 
                        if 'id_device' not in data_sync_dict:
                            return -1 
                        if 'modbusdevice' not in data_sync_dict:
                            return -1 
                        if 'data' not in data_sync_dict:
                            return -1 
                        if 'filename' not in data_sync_dict:
                            return -1
                        if 'source' not in data_sync_dict:
                            return -1
                        if 'data' not in data_sync_dict:
                            return -1
                        
                        time_id_temp = data_sync_dict['id']        
                        id_device_temp = data_sync_dict['id_device']
                        modbusdevice_temp = data_sync_dict['modbusdevice']
                        file_name_temp = data_sync_dict['filename']  
                        source_temp = data_sync_dict['source']
                        datasql_temp = data_sync_dict['data']
                        
                        data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp}
                        if len(datasql_temp) == 0 :
                            upErr_Database(time_id_temp,id_device_temp) 
                except Exception as e: 
                    print('An exception occurred',e)
            else :
                data_sent_server = data_sent_server
            # Step 2 : Sent data to server 
            if data_sent_server : 
                if 'id' not in data_sent_server:
                    return -1 
                if 'id_device' not in data_sent_server:
                    return -1 
                if 'modbusdevice' not in data_sent_server:
                    return -1 
                if 'data_sql' not in data_sent_server:
                    return -1
                
                if (len(str(data_sent_server['id_device'])) > 0
                    and len(str(data_sent_server['modbusdevice'])) > 0
                    and len(data_sent_server["data_sql"]) > 0):
                    if isinstance(data_sent_server['id'], datetime.datetime):
                        data_sent_server['id'] = data_sent_server['id'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        pass
                    data_sent_server["data_sql"] = data_sent_server["data_sql"].strip("'") 
                    device.time_id = data_sent_server['id']
                    device.id_device = data_sent_server["id_device"]
                    device.file_name = data_sent_server["filename"]
                    device.source = data_sent_server["source"]
                    device.datasql = data_sent_server["data_sql"]
                    if device.file_name and os.path.exists( device.source):
                        with open(device.source, 'r') as file:
                            device.file_content = file.read()
                            device.file_size = os.path.getsize(device.source)
                            if device.file_size > 0 :
                                device.data_file = {'file_name': device.file_name, 'file_content': device.file_content}
                            else :
                                if len(data_sent_server["id"])> 0 :
                                    upErr_Database(device.time_id,device.id_device)
                                    by_pass = 1 
                                else:
                                    pass
                    else:
                        upErr_Database(device.time_id,device.id_device)
                        by_pass = 1    
                    if device.data_file : 
                        array_file = device.file_content.split(',')

                        if name_serial_device :
                            # ==================================Information sent json to server ==================================
                            json_data = {
                            "id_channel": id_device_fr_sys,
                            "id_device": device.id_device,
                            "serial_number_port" : name_serial_device,
                            "datetime": current_time,
                            'datas': {
                                "time": array_file[0] if len(array_file) > 0 else None,
                                "error": array_file[1] if len(array_file) > 1 else None,
                                "high_alarm": array_file[2] if len(array_file) > 2 else None,
                                "low_alarm": array_file[3] if len(array_file) > 3 else None
                            }
                        }
                            # ==================================Information sent json to server ==================================
                        else :
                            pass
                    template_names = MySQL_Select(QUERY_SELECT_NAME_DEVICE, (device.id_device,))

                    if template_names : 
                        for i in range(4, len(array_file)):
                            if i - 4 < len(template_names):
                                key = template_names[i-4]
                                value = array_file[i] if array_file[i] else None
                                json_data["datas"][key['id_pointkey']] = value
                            else:
                                print(f"Not enough elements in template_names for number {i}")
                    try:
                        if json_data or files:
                            if type_file == "URL" :
                                response = requests.post(url, json=json_data) 
                                
                            if response.status_code == 200:
                                print(f"Send json {json_data_total} to the path {url} and receive feedback as {response.status_code}") 
                                print("="*40 , json_data , "="*40)
                                # Step 3 : update data error in database
                                MySQL_Update_V1(QUERY_UPDATE_DATABASE,( current_time, device.time_id, id_device_fr_sys ,device.id_device))
                                try :
                                    print("="*40, "Reponse", "="*40)
                                    print(response.json())
                                    status_sync = 1
                                    count = 0 
                                except json.JSONDecodeError:
                                    print("Empty response")
                            else:
                                print(response.json())
                                status_sync = 0
                                Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                    except Exception as e:
                        status_sync = 0 
                        Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                        print('An exception occurred ',e)
            else : 
                if len(data_sent_server["id"])> 0  :
                    upErr_Database(device.time_id,device.id_device)
                pass
        else :# There are a lot of files 
            try :
                if id_device_fr_sys :
                    data_sync_server = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,id_device,))
                if data_sync_server :
                    for item in data_sync_server :
                        data_sync_dict = item 
                        
                        time_id_temp = data_sync_dict['id']        
                        id_device_temp = data_sync_dict['id_device']
                        modbusdevice_temp = data_sync_dict['modbusdevice']
                        file_name_temp = data_sync_dict['filename']  
                        source_temp = data_sync_dict['source']
                        datasql_temp = data_sync_dict['data']
                        ensuredir_temp = data_sync_dict['ensuredir']
                        
                        data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp,"ensuredir": ensuredir_temp}
                        data_sent_server_list.append(data_sent_server)
                        if len(data_sent_server_list) == number_device :
                            for i in range(number_device): 
                                if len(str(data_sent_server_list[i]["modbusdevice"])) == 0 or len(data_sent_server_list[i]["data_sql"]) == 0 :
                                    upErr_Database(data_sent_server_list[i]["id"],data_sent_server_list[i]["id_device"]) 
            except Exception as e: 
                print('An exception occurred SQL',e)
            else :
                pass
                data_sent_server_list = data_sent_server_list
            #Step 2 : Sent data to server 
            if (len(data_sent_server_list) == 10 and data_sent_server_list ): 
                if (len(str(data_sent_server_list[i]['id_device'])) > 0 and len(str(data_sent_server_list[i]['modbusdevice'])) > 0 and len(data_sent_server_list[i]["data_sql"]) > 0 ):
                    
                    for i in range(number_device): 
                        if isinstance(data_sent_server_list[i]['id'], datetime.datetime):
                            data_sent_server_list[i]['id'] = data_sent_server_list[i]['id'].strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            pass
                        data_sent_server_list[i]["data_sql"] = data_sent_server_list[i]["data_sql"].strip("'") 
                        
                        devices[i].time_id = data_sent_server_list[i]["id"]
                        devices[i].id_device = data_sent_server_list[i]["id_device"]
                        devices[i].file_name = data_sent_server_list[i]["filename"]
                        devices[i].source = data_sent_server_list[i]["source"]
                        devices[i].datasql = data_sent_server_list[i]["data_sql"]
                        devices[i].ensuredir = data_sent_server_list[i]["ensuredir"]
                        
                        if devices[i].file_name and os.path.exists(devices[i].source):
                            with open(devices[i].source, 'r') as file:
                                devices[i].file_content = file.read()
                                devices[i].file_size = os.path.getsize(devices[i].source)
                                if devices[i].file_size > 0 and devices[i].file_content == devices[i].datasql:
                                    pass
                                else :
                                    # upErr_Database(devices[i].time_id,devices[i].id_device)
                                    by_pass = 1 
                        else:
                            upErr_Database(devices[i].time_id,devices[i].id_device)
                            by_pass = 1 
                                
                        array_file = devices[i].file_content.split(',')
                        # Collect data and after successfully sending data, update it into the database 
                        data_insert_many_temp = (current_time,devices[i].time_id ,id_device_fr_sys , devices[i].id_device)
                        data_insert_many.append(data_insert_many_temp)
                        # Collect information when an error occurs and update the number of errors to the database
                        val = (count,devices[i].time_id ,id_device_fr_sys ,devices[i].id_device)
                        if count > 0 :
                            vals.append(val)
                        # Creates a JSON object based on the array of data from the current device
                        if name_serial_device : 
                        # ==================================Information sent json to server ==================================
                            json_data_total = {
                                "id_channel": id_device_fr_sys,
                                "id_device": devices[i].id_device,
                                "serial_number_port": name_serial_device,
                                "datetime": current_time,
                                "datas": {
                                    "time": array_file[0] if array_file and len(array_file) > 0 else None,
                                    "error": array_file[1] if array_file and len(array_file) > 1 else None,
                                    "high_alarm": array_file[2] if array_file and len(array_file) > 2 else None,
                                    "low_alarm": array_file[3] if array_file and len(array_file) > 3 else None
                                }
                            }
                        # ==================================Information sent json to server ==================================
                        else :
                            pass

                        template_names = MySQL_Select(QUERY_SELECT_NAME_DEVICE, (devices[i].id_device,))

                        # Add the key to the sent json file
                        for i in range(4, len(array_file)):
                            if i - 4 < len(template_names):
                                key = template_names[i-4]
                                value = array_file[i] if array_file[i] else None
                                json_data_total["datas"][key['id_pointkey']] = value
                            else:
                                # print(f"Not enough elements in template_names for index {i}")
                                pass
                        try:
                            if json_data_total:
                                if type_file == "URL" :
                                    response = requests.post(url, json=json_data_total)
                                    print(f"Send json {json_data_total} to the path {url} and receive feedback as {response.status_code}") 
                                if response.status_code == 200:
                                    # Step 3 : update data sync in database
                                    MySQL_Update_v2(QUERY_UPDATE_DATABASE,data_insert_many)
                                    try :
                                        print("="*40, "Response ", "="*40)
                                        print(response.json())
                                        status_sync = 1
                                        count = 0 
                                    except json.JSONDecodeError:
                                        print("Empty response")
                                else:
                                    Executeup_NumberRetry_Database_Multies(time_retry)
                                    print(response.json())
                                    status_sync = 0
                        except Exception as e:
                            Executeup_NumberRetry_Database_Multies(time_retry)
                            status_sync = 0 
                            print('An exception occurred ',e)
                    else : 
                        if i < len(devices) and len(devices[i].time_id) > 0 and len(str(devices[i].id_device)) > 0:
                            upErr_Database(devices[i].time_id,devices[i].id_device)
                        else :
                            pass
    else : 
        pass
# Describe sync_ServerFile_Database_AllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_ServerFile_Database_AllDevice():
    global id_upload_chanel
    global QUERY_ALL_DEVICES_SYNCDATA
    id_device_fr_sys = id_upload_chanel[1]
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (id_device_fr_sys,))
    
    tasks = []
    for item in result_all:
        sql_id = item["id"]
        task = sync_ServerFile_Database(sql_id)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
# Describe sync_Server_Database
# /**
# 	 * @description read data from database , send data to server , update data sent in database
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_ServerFile_Database(sql_id):
    # Step 1 : Read data from database 
    current_time = get_utc()
    global id_upload_chanel
    global data_sent_server
    global status_sync
    global count
    global multifile
    global time_retry
    global vals
    global json_data 
    global number_device
    global array_file
    
    global QUERY_SYNC_SERVER
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_DATABASE
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    global QUERY_SELECT_NAME_DEVICE
    global QUERY_SELECT_SERIAL_NUMBER
    global QUERY_SELECT_URL
    global QUERY_TIME_SYNC_DATA
    global QUERY_SYNC_FILELOG_SERVER
    global QUERY_ALL_DEVICES_SYNCDATA
    
    id_device_fr_sys = id_upload_chanel[1]
    data_sync_server = []
    data_sent_server_list = []
    data_sync_dict = []
    devices = []
    file = []
    files = []
    data_insert_many_temp = []
    data_insert_many = []
    val = []
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    result1 =[]
    result2 =[]
    result3 =[]
    
    file = {}
    
    name_serial_device = ""
    number_file = ""
    url = ""
    response = ""
    merged_content = ""
    server_response_text = ""
    count_merged = 0

    class MyVariable3:
        def __init__(self, time_id, id_device, modbusdevice, source, ensuredir, file_name, file_content, file_size, datasql, data_file):
            self.time_id = time_id
            self.id_device = id_device
            self.modbusdevice = modbusdevice
            self.source = source
            self.ensuredir = ensuredir
            self.file_name = file_name
            self.file_content = file_content
            self.file_size = file_size
            self.datasql = datasql
            self.data_file = data_file

    for _ in range(number_device):
        device = MyVariable3("", "", "", "", "","", "", 0 , "", "")
        devices.append(device)
    
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]
        
    result1 = MySQL_Select(QUERY_NUMER_FILE,(id_device_fr_sys,))
    number_file = result1[0]["remaining_files"]
    
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    
    if number_file <= len(result_all)*2 :
        multifile = False 
    else :
        multifile = True 
    
    result2 = await MySQL_Select_v1(QUERY_SELECT_SERIAL_NUMBER)
    name_serial_device = result2[0]["serial_number"] 
    
    result3 = MySQL_Select(QUERY_SELECT_URL,(id_device_fr_sys,))
    url = result3[0]["uploadurl"]
    
    result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
    # execute devices in the list simultaneously
    if number_file != 0 and url:
        if multifile is False :
            if count == 0 :
                try :
                    data_sync_server = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,sql_id,))
                    if data_sync_server :
                        data_sync_dict = data_sync_server[0]
                        if 'id' not in data_sync_dict:
                            return -1 
                        if 'id_device' not in data_sync_dict:
                            return -1 
                        if 'modbusdevice' not in data_sync_dict:
                            return -1 
                        if 'data' not in data_sync_dict:
                            return -1 
                        if 'filename' not in data_sync_dict:
                            return -1
                        if 'source' not in data_sync_dict:
                            return -1
                        if 'data' not in data_sync_dict:
                            return -1
                        
                        time_id_temp = data_sync_dict['id']        
                        id_device_temp = data_sync_dict['id_device']
                        modbusdevice_temp = data_sync_dict['modbusdevice']
                        file_name_temp = data_sync_dict['filename']  
                        source_temp = data_sync_dict['source']
                        datasql_temp = data_sync_dict['data']
                        
                        data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp}
                        if len(datasql_temp) == 0 :
                            upErr_Database(time_id_temp,id_device_temp) 
                except Exception as e: 
                    print('An exception occurred',e)
            else :
                data_sent_server = data_sent_server
            # Step 2 : Sent data to server 
            if data_sent_server : 
                if 'id' not in data_sent_server:
                    return -1 
                if 'id_device' not in data_sent_server:
                    return -1 
                if 'modbusdevice' not in data_sent_server:
                    return -1 
                if 'data_sql' not in data_sent_server:
                    return -1
                
                if (len(str(data_sent_server['id_device'])) > 0
                    and len(str(data_sent_server['modbusdevice'])) > 0
                    and len(data_sent_server["data_sql"]) > 0):
                    if isinstance(data_sent_server['id'], datetime.datetime):
                        data_sent_server['id'] = data_sent_server['id'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        pass
                    data_sent_server["data_sql"] = data_sent_server["data_sql"].strip("'") 
                    device.time_id = data_sent_server['id']
                    device.id_device = data_sent_server["id_device"]
                    device.file_name = data_sent_server["filename"]
                    device.source = data_sent_server["source"]
                    device.datasql = data_sent_server["data_sql"]
                    if device.file_name and os.path.exists( device.source):
                        with open(device.source, 'r') as file:
                            device.file_content = file.read()
                            device.file_size = os.path.getsize(device.source)
                            if device.file_size > 0 :
                                device.data_file = {'file_name': device.file_name, 'file_content': device.file_content}
                            else :
                                if len(data_sent_server["id"])> 0  :
                                    upErr_Database(device.time_id,device.id_device)
                                    by_pass = 1 
                                else:
                                    pass
                    else:
                        upErr_Database(device.time_id,device.id_device)
                        by_pass = 1    
                    if os.path.exists(device.source):     
                        
                        # ==================================Information sent file to server ==================================
                        headers = {
                            'SERIALNUMBER': name_serial_device,
                            'MODBUSDEVICE': device.id_device,
                            'MODBUSPORT': device.id_device,
                            'MODE': 'LOGFILEUPLOAD'
                        }
                        file = ('LOGFILE', (device.file_name, open(device.source, 'rb'), 'text/plain'))
                        files.append(file)

                        # ==================================Information sent file to server ==================================
                    else:
                        upErr_Database(device.time_id,device.id_device)
                    try:
                        if json_data or files:
                            response = requests.post(url, files=files , data=headers)
                            server_response_text = response.text
                            print(f"Send file {device.file_name} to the path {url} and receive feedback as {server_response_text}") 
                            # print("repr(server_response_text)", repr(server_response_text))
                        if response.text == "\nSUCCESS\n":
                            # Step 3 : update data error in database
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,( current_time, device.time_id, id_device_fr_sys ,device.id_device))
                            status_sync = 1
                            count = 0 
                        else:
                            status_sync = 0
                            Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                    except Exception as e:
                        status_sync = 0 
                        Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                        print('An exception occurred ',e)
            else : 
                if len(data_sent_server["id"])> 0  :
                    upErr_Database(device.time_id,device.id_device)
                pass
        else :# There are a lot of files 
            try :
                if id_device_fr_sys :
                    data_sync_server = MySQL_Select(QUERY_SYNC_FILELOG_SERVER,(id_device_fr_sys,sql_id,))
                if data_sync_server :
                    for item in data_sync_server :
                        data_sync_dict = item 
                        
                        time_id_temp = data_sync_dict['id']        
                        id_device_temp = data_sync_dict['id_device']
                        modbusdevice_temp = data_sync_dict['modbusdevice']
                        file_name_temp = data_sync_dict['filename']  
                        source_temp = data_sync_dict['source']
                        datasql_temp = data_sync_dict['data']
                        ensuredir_temp = data_sync_dict['ensuredir']
                        
                        data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp,"ensuredir": ensuredir_temp}
                        data_sent_server_list.append(data_sent_server)
                        if len(data_sent_server_list) == number_device :
                            for i in range(number_device): 
                                if len(str(data_sent_server_list[i]["modbusdevice"])) == 0 or len(data_sent_server_list[i]["data_sql"]) == 0 :
                                    upErr_Database(data_sent_server_list[i]["id"],data_sent_server_list[i]["id_device"]) 
            except Exception as e: 
                print('An exception occurred SQL',e)
            else :
                pass
                data_sent_server_list = data_sent_server_list
            #Step 2 : Sent data to server 
            if data_sent_server_list: 
                # if (len(str(data_sent_server_list[i]['id_device'])) > 0 and len(str(data_sent_server_list[i]['modbusdevice'])) > 0 and len(data_sent_server_list[i]["data_sql"]) > 0 ):
                    
                for i in range(min(number_device, len(data_sent_server_list))):  
                    if isinstance(data_sent_server_list[i]['id'], datetime.datetime):
                        data_sent_server_list[i]['id'] = data_sent_server_list[i]['id'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        pass
                    data_sent_server_list[i]["data_sql"] = data_sent_server_list[i]["data_sql"].strip("'") 
                    devices[i].time_id = data_sent_server_list[i]["id"]
                    devices[i].id_device = data_sent_server_list[i]["id_device"]
                    devices[i].file_name = data_sent_server_list[i]["filename"]
                    devices[i].source = data_sent_server_list[i]["source"]
                    devices[i].datasql = data_sent_server_list[i]["data_sql"]
                    devices[i].ensuredir = data_sent_server_list[i]["ensuredir"]
                    
                    if devices[i].file_name and os.path.exists(devices[i].source):
                        with open(devices[i].source, 'r') as file:
                            devices[i].file_content = file.read()
                            devices[i].file_size = os.path.getsize(devices[i].source)
                            if devices[i].file_size > 0 and devices[i].file_content == devices[i].datasql:
                                pass
                            else :
                                # upErr_Database(devices[i].time_id,devices[i].id_device)
                                by_pass = 1 
                    else:
                        upErr_Database(devices[i].time_id,devices[i].id_device)
                        by_pass = 1 
                            
                    array_file = devices[i].file_content.split(',')
                    # Accumulate the contents of 10 files into a single file
                    merged_content += ','.join(array_file) + '\n'
                    count_merged += 1
                    # Create the full path to the file
                    current_time = get_utc()
                    time_file_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
                    formatted_time1 = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
                    file_name = f'{"mb"}-{devices[i].id_device:03d}.{formatted_time1}.log'
                    file_path = devices[i].ensuredir
                    source_file = os.path.join(file_path, file_name)

                    # Write content from merged_content to the created file
                    with open(source_file, 'w', encoding='utf-8') as file:
                        file.write(merged_content)
                    # ==================================Information sent file to server==================================
                    headers = {
                        'SERIALNUMBER': name_serial_device,
                        'MODBUSDEVICE': devices[i].id_device,
                        'MODBUSPORT': devices[i].id_device,
                        'MODE': 'LOGFILEUPLOAD'
                    }

                    # Collect data and after successfully sending data, update it into the database
                    data_insert_many_temp = (current_time,devices[i].time_id ,id_device_fr_sys , devices[i].id_device)
                    data_insert_many.append(data_insert_many_temp)
                    # Collect information when an error occurs and update the number of errors to the database
                    val = (count,devices[i].time_id ,id_device_fr_sys ,devices[i].id_device)
                    if count > 0 :
                        vals.append(val)
                try:
                    if source_file and file_name:
                        file = ('LOGFILE', (file_name, open(source_file, 'rb'), 'text/plain'))
                        files.append(file)
                        # Send the file to the server and wait for a 200 response
                        response = requests.post(url, files=files, data=headers)
                        server_response_text = response.text
                        print(f"Send file {device.file_name} to the path {url} and receive feedback as {server_response_text}") 
                        
                        if server_response_text == "\nSUCCESS\n":
                            # Step 3 : update data sync in database
                            MySQL_Update_v2(QUERY_UPDATE_DATABASE,data_insert_many)
                            count_merged = 0
                            merged_content = ""
                            status_sync = 1
                            count = 0 
                        else:
                            Executeup_NumberRetry_Database_Multies(time_retry)
                            status_sync = 0
                except Exception as e:
                    Executeup_NumberRetry_Database_Multies(time_retry)
                    status_sync = 0 
                    print('An exception occurred ',e)
                else : 
                    if i < len(devices) and len(devices[i].time_id) > 0 and len(str(devices[i].id_device)) > 0:
                        upErr_Database(devices[i].time_id,devices[i].id_device)
                    else :
                        pass
    else :
        pass
# Describe upNumberRetry_Database
# /**
# 	 * @description write number retry in database
# 	 * @author bnguyen
# 	 * @since 10-1-2023
# 	 * @param {}
# 	 * @return MySQL_Update_V1(QUERY_TIME_RETRY,(count , Time ,id_device_fr_sys , id_device))
# 	 */                  
async def sync_ServerFTP_Database(FTPSERVER_HOSTNAME,FTPSERVER_PORT,FTPSERVER_USERNAME,FTPSERVER_PASSWORD):
    # Step 1 : Read data from database 
    current_time = get_utc()
    
    global id_upload_chanel
    global data_sent_server
    global status_sync
    global count
    global multifile
    global count_FTP_Server
    global isUploadSuccess
    global vals
    
    global QUERY_SYNC_SERVER
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_DATABASE
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    
    id_device_fr_sys = id_upload_chanel[1]
    data_sync_server = []
    data_sent_server_list = []
    data_sync_dict = []
    devices = []
    data_insert_many_temp = []
    data_insert_many = []
    val = []
    
    number_file = 0 
    by_pass = 0 
    file = {}
    
    class MyVariable2:
        def __init__(self, time_id, id_device, modbusdevice, source, file_name, file_content, file_size, datasql, data_file):
            self.time_id = time_id
            self.id_device = id_device
            self.modbusdevice = modbusdevice
            self.source = source
            self.file_name = file_name
            self.file_content = file_content
            self.file_size = file_size
            self.datasql = datasql
            self.data_file = data_file

    for _ in range(number_device):
        device = MyVariable2("", "", "", "", "", "", 0 , "", "")
        devices.append(device)

    result1 = MySQL_Select(QUERY_NUMER_FILE,(id_device_fr_sys,))
    number_file = result1[0]["remaining_files"]
    if number_file <= 400 :
        multifile = False 
    else :
        multifile = True 
        
    if multifile is False and number_file != 0 :
        if count == 0 :
            try :
                data_sync_server = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,))
                if data_sync_server :
                    data_sync_dict = data_sync_server[0]
                    if 'id' not in data_sync_dict:
                        return -1 
                    if 'id_device' not in data_sync_dict:
                        return -1 
                    if 'modbusdevice' not in data_sync_dict:
                        return -1 
                    if 'data' not in data_sync_dict:
                        return -1 
                    if 'filename' not in data_sync_dict:
                        return -1
                    if 'source' not in data_sync_dict:
                        return -1
                    if 'data' not in data_sync_dict:
                        return -1
                    
                    time_id_temp = data_sync_dict['id']        
                    id_device_temp = data_sync_dict['id_device']
                    modbusdevice_temp = data_sync_dict['modbusdevice']
                    file_name_temp = data_sync_dict['filename']  
                    source_temp = data_sync_dict['source']
                    datasql_temp = data_sync_dict['data']
                    
                    data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp}
                    if len(datasql_temp) == 0 :
                        upErr_Database(time_id_temp,id_device_temp) 
            except Exception as e: 
                print('An exception occurred',e)
        else :
            data_sent_server = data_sent_server
        # Step 2 : Sent data to server 
        if data_sent_server : 
            if 'id' not in data_sent_server:
                return -1 
            if 'id_device' not in data_sent_server:
                return -1 
            if 'modbusdevice' not in data_sent_server:
                return -1 
            if 'data_sql' not in data_sent_server:
                return -1
            
            if (len(str(data_sent_server['id_device'])) > 0
                and len(str(data_sent_server['modbusdevice'])) > 0
                and len(data_sent_server["data_sql"]) > 0):
                if isinstance(data_sent_server['id'], datetime.datetime):
                    data_sent_server['id'] = data_sent_server['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                data_sent_server["data_sql"] = data_sent_server["data_sql"].strip("'") 
                device.time_id = data_sent_server['id']
                device.id_device = data_sent_server["id_device"]
                device.file_name = data_sent_server["filename"]
                device.source = data_sent_server["source"]
                device.datasql = data_sent_server["data_sql"]
                if device.file_name and os.path.exists( device.source):
                    with open( device.source, 'r') as file:
                        device.file_content = file.read()
                        device.file_size = os.path.getsize(device.source)
                        if device.file_size > 0 :
                            device.data_file = {'file_name': device.file_name, 'file_content': device.file_content}
                        else :
                            if len(data_sent_server["id"])> 0 :
                                upErr_Database(device.time_id,device.id_device)
                                by_pass = 1 
                            else:
                                pass
                else:
                    upErr_Database(device.time_id,device.id_device)
                    by_pass = 1   
                try:
                    if data_sent_server and by_pass == 0 :
                        # Step 2 : Sent File to FTP Server
                        isUploadSuccess = uploadFileToFtp(device.source,FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD)
                        if isUploadSuccess == True :
                            # Step 3 : Updata sync server with database
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,( current_time, device.time_id, id_device_fr_sys ,device.id_device))
                            status_sync = 1
                            count = 0 
                            print("gửi file thành công " , device.file_name)
                        else :
                            status_sync = 0
                            Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                    else :
                        pass 
                except Exception as e:
                    status_sync = 0 
                    Executeup_NumberRetry_Database(time_retry,device.time_id,device.id_device)
                    print('An exception occurred',e)
        else : 
            if len(data_sent_server["id"])> 0 :
                upErr_Database(device.time_id,device.id_device)
            pass
    elif multifile is False and number_file != 0 :
        print("che do ftp nhieu file")
        try :
            data_sync_server = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,id_device_fr_sys))
            if data_sync_server :
                for item in data_sync_server :
                    data_sync_dict = item 
                    
                    time_id_temp = data_sync_dict['id']        
                    id_device_temp = data_sync_dict['id_device']
                    modbusdevice_temp = data_sync_dict['modbusdevice']
                    file_name_temp = data_sync_dict['filename']  
                    source_temp = data_sync_dict['source']
                    datasql_temp = data_sync_dict['data']
                    
                    data_sent_server = {"id": time_id_temp, "id_device": id_device_temp, "modbusdevice": modbusdevice_temp, "filename": file_name_temp,"source": source_temp,"data_sql": datasql_temp}
                    data_sent_server_list.append(data_sent_server)
                    if len(data_sent_server_list) == number_device :
                        for i in range(number_device): 
                            if len(str(data_sent_server_list[i]["modbusdevice"])) == 0 or len(data_sent_server_list[i]["data_sql"]) == 0 :
                                upErr_Database(data_sent_server_list[i]["id"],data_sent_server_list[i]["id_device"]) 
        except Exception as e: 
            print('An exception occurred SQL',e)
        else :
            pass
            data_sent_server_list = data_sent_server_list
        #Step 2 : Sent data to server 
        if (len(data_sent_server_list) == 10 and data_sent_server_list ): 
            if (len(str(data_sent_server_list[i]['id_device'])) > 0 and len(str(data_sent_server_list[i]['modbusdevice'])) > 0 and len(data_sent_server_list[i]["data_sql"]) > 0 ):
                
                for i in range(number_device): 
                    if isinstance(data_sent_server_list[i]['id'], datetime.datetime):
                        data_sent_server_list[i]['id'] = data_sent_server_list[i]['id'].strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        pass
                    data_sent_server_list[i]["data_sql"] = data_sent_server_list[i]["data_sql"].strip("'") 
                    
                    devices[i].time_id = data_sent_server_list[i]["id"]
                    devices[i].id_device = data_sent_server_list[i]["id_device"]
                    devices[i].file_name = data_sent_server_list[i]["filename"]
                    devices[i].source = data_sent_server_list[i]["source"]
                    devices[i].datasql = data_sent_server_list[i]["data_sql"]

                    if devices[i].file_name and os.path.exists(devices[i].source):
                        with open(devices[i].source, 'r') as file:
                            devices[i].file_content = file.read()
                            devices[i].file_size = os.path.getsize(devices[i].source)
                            if devices[i].file_size > 0 and devices[i].file_content == devices[i].datasql:
                                pass
                            else :
                                # upErr_Database(devices[i].time_id,devices[i].id_device)
                                by_pass = 1 
                    else:
                        upErr_Database(devices[i].time_id,devices[i].id_device)
                        by_pass = 1 
                    
                    data_insert_many_temp = (current_time,devices[i].time_id ,id_device_fr_sys , devices[i].id_device)
                    data_insert_many.append(data_insert_many_temp)
                    
                    val = (count,devices[i].time_id ,id_device_fr_sys ,devices[i].id_device)
                    if count > 0 :
                        vals.append(val)

def uploadFileToFtp(localFilePath,ftpHost, ftpPort, ftpUname, ftpPass):
    
    isUploadSuccess = False  
    global time_retry 
    
    if os.path.exists(localFilePath):
        # Connect to the FTP server
        ftp = ftplib.FTP(timeout=30)
        ftp.connect(ftpHost, ftpPort)
        ftp.login(ftpUname, ftpPass)
        # Retrieve the list of directories on the FTP server
        directories = []
        ftp.retrlines('LIST', lambda x: directories.append(x.split()[-1]))
        for directory in directories:
            chosenDirectory = directory  

        # Change to the specified remote directory
        if chosenDirectory:
            ftp.cwd(chosenDirectory)

            file_size = os.path.getsize(localFilePath)

            if file_size > 0:
                _, targetFilename = os.path.split(localFilePath)
                with open(localFilePath, "rb") as file:
                    retCode = ftp.storbinary(f"STOR {targetFilename}", file, blocksize=1024*1024)
                if retCode.startswith('226'):
                    isUploadSuccess = True
                else:
                    isUploadSuccess = False
                # Close the FTP connection
                ftp.quit()

            else:
                print("File size is 0. The file will not be uploaded.")
    else:
        print("Invalid local file path: {0}".format(localFilePath))
    return isUploadSuccess
# Describe sync_Server_Database
# /**
# 	 * @description execute when systemp is fault 
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
def Executeup_NumberRetry_Database(time_retry, Time, id_device):
    global count
    global status_sync
    global flag_end_update

    if count <= 4:
        count += 1
    if status_sync == 1:
        count = 0
        flag_end_update = False
        pass
    if len(Time) and len(str(id_device)) and flag_end_update == False :
        if count != 0 and status_sync == 0:
            if 1 <= time_retry <= 15 and status_sync == 0:
                scheduler = AsyncIOScheduler()
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time, id_device])
                scheduler.start()
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
            elif time_retry == -1:
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
                pass
            elif time_retry == 0:  # test
                scheduler = AsyncIOScheduler()
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time, id_device])
                scheduler.start()
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
            else:
                pass
        else:
            pass
    else:
        pass
# Describe Executeup_NumberRetry_Database_Multies
# /**
# 	 * @description execute when systemp is fault 
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
def Executeup_NumberRetry_Database_Multies(time_retry):
    global count
    global status_sync
    global flag_end_update

    if count <= 4:
        count += 1
    if status_sync == 1:
        count = 0
        flag_end_update = False
        pass
    
    if flag_end_update == False :
        if count != 0 and status_sync == 0:
            if 1 <= time_retry <= 15 and status_sync == 0:
                scheduler = AsyncIOScheduler()
                scheduler.add_job(upNumberRetry_Database_Multies, 'cron', minute=time_retry)
                scheduler.start()
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
            elif time_retry == -1:
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
                pass
            elif time_retry == 0:  # test
                scheduler = AsyncIOScheduler()
                scheduler.add_job(upNumberRetry_Database_Multies, 'cron', second="*/3")
                scheduler.start()
                if count == 5:
                    flag_end_update = True
                    scheduler.shutdown()
            else:
                pass
        else:
            pass
    else:
        pass
# Describe upNumberRetry_Database
# /**
# 	 * @description write number retry in database
# 	 * @author bnguyen
# 	 * @since 10-1-2023
# 	 * @param {}
# 	 * @return MySQL_Update_V1(QUERY_TIME_RETRY,(count , Time ,id_device_fr_sys , id_device))
# 	 */                  
def upNumberRetry_Database(Time,id_device):
    global count
    global status_sync 
    global id_upload_chanel
    global QUERY_UPDATE_NUMBERRETRY
    id_device_fr_sys = id_upload_chanel[1]
    
    if status_sync == 0:
        try: 
            
            MySQL_Update_V1(QUERY_UPDATE_NUMBERRETRY,(count , Time ,id_device_fr_sys , id_device))
        except Exception as e:
            print('An exception occurred',e)
    else :
        pass
# Describe upNumberRetry_Database
# /**
# 	 * @description write number retry in database
# 	 * @author bnguyen
# 	 * @since 10-1-2023
# 	 * @param {}
# 	 * @return MySQL_Update_V1(QUERY_TIME_RETRY,(count , Time ,id_device_fr_sys , id_device))
# 	 */                  
def upNumberRetry_Database_Multies():
    global status_sync 
    global id_upload_chanel
    global count
    global QUERY_UPDATE_NUMBERRETRY
    global vals
    if status_sync == 0 and count > 0:
        try: 
            MySQL_Update_v2(QUERY_UPDATE_NUMBERRETRY,(vals))
            vals = []
        except Exception as e:
            print('An exception occurred',e)
    else :
        pass
# Describe upData_Database
# /**
# 	 * @description check file empty by pass
# 	 * @author bnguyen
# 	 * @since 10-1-2023
# 	 * @param {}
# 	 * @return MySQL_Update_V1(QUERY_UPDATE_ERR_DATABASE,(Time ,id_device_fr_sys , id_device))
# 	 */              
def upErr_Database(Time,id_device):
    global id_upload_chanel
    id_device_fr_sys = id_upload_chanel[1]
    global QUERY_UPDATE_ERR_DATABASE
    try: 
        MySQL_Update_V1(QUERY_UPDATE_ERR_DATABASE,(Time ,id_device_fr_sys , id_device))
    except Exception as e:
        print('An exception occurred',e)

async def main():
    global id_upload_chanel
    global multifile
    global time_retry
    global type_file
    global serial_number
    global time_sentdata
    global int_number
    
    global QUERY_ALL_DEVICES_SYNCDATA
    global QUERY_GETDATA_SERVER
    global QUERY_SYNC_SERVER
    global QUERY_UPDATE_DATABASE
    global QUERY_TIME_SYNC_DATA
    global QUERY_UPDATE_ERR_DATABASE
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_NUMBERRETRY
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    global QUERY_SYNC_ERROR_MQTT
    global QUERY_SELECT_NAME_DEVICE
    global QUERY_UPDATE_SERIAL_NUMBER
    global QUERY_SELECT_SERIAL_NUMBER
    global QUERY_SELECT_URL
    global QUERY_SYNC_FILELOG_SERVER
    global QUERY_TIME_CREATE_FILE
    global QUERY_SELECT_TOPIC
    
    result_all =[]
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_ALL_DEVICES_SYNCDATA = result_mybatis["QUERY_ALL_DEVICES_SYNCDATA"] # ok 
        QUERY_GETDATA_SERVER = result_mybatis["QUERY_GETDATA_SERVER"] 
        QUERY_SYNC_SERVER = result_mybatis["QUERY_SYNC_SERVER"]
        QUERY_UPDATE_DATABASE = result_mybatis["QUERY_UPDATE_DATABASE"]
        QUERY_TIME_SYNC_DATA = result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_UPDATE_ERR_DATABASE = result_mybatis["QUERY_UPDATE_ERR_DATABASE"]
        QUERY_TIME_RETRY = result_mybatis["QUERY_TIME_RETRY"]
        QUERY_UPDATE_NUMBERRETRY = result_mybatis["QUERY_UPDATE_NUMBERRETRY"]
        QUERY_NUMER_FILE = result_mybatis["QUERY_NUMER_FILE"]
        QUERY_SYNC_MULTIFILE_SERVER = result_mybatis["QUERY_SYNC_MULTIFILE_SERVER"]
        QUERY_SYNC_ERROR_MQTT = result_mybatis["QUERY_SYNC_ERROR_MQTT"]
        QUERY_SELECT_NAME_DEVICE = result_mybatis["QUERY_SELECT_NAME_DEVICE"]
        QUERY_UPDATE_SERIAL_NUMBER = result_mybatis["QUERY_UPDATE_SERIAL_NUMBER"]
        QUERY_SELECT_SERIAL_NUMBER = result_mybatis["QUERY_SELECT_SERIAL_NUMBER"]
        QUERY_SELECT_URL = result_mybatis["QUERY_SELECT_URL"]
        QUERY_SYNC_FILELOG_SERVER = result_mybatis["QUERY_SYNC_FILELOG_SERVER"]
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_SELECT_TOPIC = result_mybatis["QUERY_SELECT_TOPIC"]
        
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_GETDATA_SERVER or not QUERY_ALL_DEVICES_SYNCDATA or not QUERY_SYNC_SERVER or not QUERY_UPDATE_DATABASE or not QUERY_TIME_SYNC_DATA or not QUERY_UPDATE_ERR_DATABASE or not QUERY_TIME_RETRY or not QUERY_UPDATE_NUMBERRETRY or not QUERY_NUMER_FILE or not QUERY_SYNC_MULTIFILE_SERVER or not QUERY_SYNC_ERROR_MQTT or not QUERY_SELECT_NAME_DEVICE or not QUERY_UPDATE_SERIAL_NUMBER or not QUERY_SELECT_SERIAL_NUMBER or not QUERY_SELECT_URL or not QUERY_SYNC_FILELOG_SERVER or not QUERY_TIME_CREATE_FILE or not QUERY_SELECT_TOPIC:
        print("Error not found data in file mybatis")
        return -1
    try: 
        result = await MySQL_Select_v1(QUERY_TIME_RETRY)
        time_retry = result[0]["time_log_data_server"]
        time_data_server = await MySQL_Select_v1(QUERY_GETDATA_SERVER)
        
        # Retrieve file synchronization time according to the log cycle.
        time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
        item = time_create_file_insert_data_table_dev[0]
        time_interval = item["time_log_interval"]
        position = time_interval.rfind("minute")
        number = time_interval[:position]
        int_number = int(number)
        id_device_fr_sys = id_upload_chanel[1]
        result_all = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(id_device_fr_sys,))
        time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
        for item in time_sync_data:
            type_file = item["type_protocol"]
        
    except Exception as e:
            print('An exception occurred',e)
    if not result_all :
        print("None of the devices have been selected in the database")
        return -1
    if not time_data_server :
        print("Unable to select synchronization time for data in the database.")
        return -1
    if type_file != "URL" and type_file != "LOG" and type_file != "FTP":
        print("Unable to select file type in the database.")
        return -1
    if time_data_server and isinstance(time_data_server[0].get("time_log_data_server"), int):
        time_sentdata = time_data_server[0]["time_log_data_server"]
        time_sentdata = int(time_sentdata)
    else:
        print("Cannot be converted to an integer.")
        return -1

    if time_sentdata and type_file == "URL":
            if 0 <= time_sentdata <= 24: # Connect by timestamp
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'cron', hour = 1,  args=[])
                scheduler.start()
            elif time_sentdata == 95 : # Connect Every 12 hours
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'interval', hours = 12,  args=[])
                scheduler.start()
            elif time_sentdata == 96 : # Connect Every 8 hours
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'interval', hours = 8,  args=[])
                scheduler.start()
            elif time_sentdata == 97 and int_number : # Connect Every Log Cycle
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'interval', minutes = int(int_number),  args=[])
                scheduler.start()
            elif time_sentdata == 98 : # Connect Every 15 minutes
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'interval', minutes = 15,  args=[])
                scheduler.start()
            elif time_sentdata == 99 : # Connect Every Hour
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'interval', hours = 1,  args=[])
                scheduler.start()
            elif time_sentdata == 100 : # test cron 
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerURL_Database_AllDevice, 'cron', second="*/10", args=[])
                scheduler.start()
    if time_sentdata and type_file == "LOG":
            if 0 <= time_sentdata <= 24: # Connect by timestamp
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'cron', hour = 1, args=[])
                scheduler.start()
            elif time_sentdata == 95 : # Connect Every 12 hours
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'interval', hours = 12, args=[])
                scheduler.start()
            elif time_sentdata == 96 : # Connect Every 8 hours
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'interval', hours = 8, args=[])
                scheduler.start()
            elif time_sentdata == 97 and int_number : # Connect Every Log Cycle
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'interval', minutes=int(int_number), args=[])
                scheduler.start()
            elif time_sentdata == 98 : # Connect Every 15 minutes
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'interval', minutes = 15, args=[])
                scheduler.start()
            elif time_sentdata == 99 : # Connect Every Hour
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'interval', hours = 1, args=[])
                scheduler.start()
            elif time_sentdata == 100 : # test cron 
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFile_Database_AllDevice, 'cron', second="*/10", args=[])
                scheduler.start()
    if time_sentdata and count <= 1 and type_file == "FTP":
            if 0 <= time_sentdata <= 24:
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'cron', hour = 1,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
            elif time_sentdata == 95 :
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = 12,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
            elif time_sentdata == 96 :
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = 8,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
            elif time_sentdata == 97 :
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'interval', minutes = int(int_number),  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
            elif time_sentdata == 98 :
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'interval', minutes = 15,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
            elif time_sentdata == 99 :
                scheduler = AsyncIOScheduler()
                scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = 1,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                scheduler.start()
        
    scheduler = AsyncIOScheduler()
    scheduler.add_job(colectDatatoPushMQTT_AllDevice, 'cron', second = "*/10" , args=[MQTT_BROKER,
                                                                                        MQTT_PORT,
                                                                                        MQTT_TOPIC_PUB,
                                                                                        MQTT_USERNAME,
                                                                                        MQTT_PASSWORD] )
    scheduler.start()
    tasks = []
    tasks.append(asyncio.create_task(subMQTT(MQTT_BROKER,
                                            MQTT_PORT,
                                            MQTT_TOPIC_SUB,
                                            MQTT_USERNAME,
                                            MQTT_PASSWORD)))
    # Move the gather outside the loop to wait for all tasks to complete
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
    asyncio.run(main())
    


