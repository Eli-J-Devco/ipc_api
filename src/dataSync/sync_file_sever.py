import asyncio
import copy
import datetime
import ftplib
import json
import logging
import os
import subprocess
import sys

import mqttools
import mybatis_mapper2sql
import paho.mqtt.publish as publish

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from configs.config import Config
from utils.libMySQL import *

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
FTP = ""

# Variables 
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/Upload" 
MQTT_TOPIC_SUB = "NgayLapTuc"
MQTT_USERNAME = Config.MQTT_USERNAME 
MQTT_PASSWORD = Config.MQTT_PASSWORD

QUERY_ALL_DEVICES = ""
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
QUERY_GET_THE_KEY = ""
QUERY_UPDATE_SERIAL_NUMBER = ""
QUERY_SELECT_SERIAL_NUMBER = ""
QUERY_SELECT_URL = ""

data_sent_server = {}
data_sent_server_list = []
array_file = []
array_files = []
json_data = {}
json_datas = {}
json_data_list = []
vals = []
data = 0
status_sync = 0 
count = 0
sync_immediately = 0 
flag_sync_immediately = False 
flag_end_update = False
flag_retry = False
count = 0 
serial_number = ""
count_FTP_Server = 0
number_file = 0
number_device = 10 
multifile = False
time_retry = ""
type_file = ""
isUploadSuccess = False

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
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
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
# Describe get serial number for system
# /**
# 	 * @description get_serial_number_windows
# 	 * @author bnguyen
# 	 * @since 27/2/2024
# 	 * @param {}
# 	 * @return serial number
# 	 */  
def get_serial_number_windows():
    try:
        # Chạy lệnh wmic để lấy thông tin SerialNumber
        result = subprocess.check_output(["wmic", "bios", "get", "serialnumber"]).decode("utf-8")
        # Lọc kết quả để chỉ lấy SerialNumber
        serial_number = result.strip().split("\n")[1]
        return serial_number
    except Exception as e:
        print(f"Lỗi khi lấy thông tin SerialNumber: {e}")
        return None
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
# 	 * @description Push data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data()
# 	 */      
def pushMQTT(host, port,topic, username, password, data_send):
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                    retain=False, port=port,
                    auth = {'username':f'{username}', 
                            'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")
        pass
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 10/1/2024
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
async def colectDatatoPushMQTT(host, port, topic, username, password):
    global id_upload_chanel
    global QUERY_TIME_SYNC_DATA
    global QUERY_SYNC_SERVER
    global QUERY_ALL_DEVICES
    global status_sync
    global multifile
    global number_device 
    global json_data
    
    data_sent_server_mqtt = []
    data_sent_server_list_mqtt = []
    data_sync_server_mqtt = []
    data_sync_dict = []
    devices = []
    data_mqtts = []

    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    id_device_fr_sys = id_upload_chanel[1]
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]
        
    class MyVariable1:
        def __init__(self, time_id, file_name, number_time_retry, id_device,id_device_str, device_name, error, result_error, status):
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

    # Push When Sent data once file 
    if multifile is False :
            data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,))
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
                data_mqtt={
                    "ID_DEVICE":device.id_device,
                    "FILE_NAME": device.file_name,
                    "TIME_STAMP": date_str,
                    "STATUS_FILE_SERVER": device.status,
                    "NUMBER_OF_RETRY":device.number_time_retry, 
                }
                pushMQTT(host,
                        port,
                        topic + f"/Channel{id_device_fr_sys}/{type_file}/"+device.id_device_str+"|"+ device.device_name,
                        username,
                        password,
                        data_mqtt)
    else :
        data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,id_device_fr_sys,))
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
                # devices[0].error = devices[0].result_error[0]["error"]
                
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
                
                data_mqtt={
                    "ID_DEVICE":devices[i].id_device,
                    "FILE_NAME": devices[i].file_name,
                    "TIME_STAMP": date_str,
                    "STATUS_FILE_SERVER": devices[i].status,
                    "NUMBER_TIME_RETRY": devices[i].number_time_retry, 
                }
                # Neu nhieu file Json 
                data_mqtts.append(data_mqtt) 
                
                pushMQTT(host,
                        port,
                        topic + f"/Channel{id_device_fr_sys}/{type_file}/"+ devices[i].id_device_str +"|"+ devices[i].device_name,
                        username,
                        password,
                        data_mqtts)
                
# Describe sync_Server_Database
# /**
# 	 * @description read data from database , send data to server , update data sent in database
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_ServerURL_Database(URL_SERVER_SYNC, URL_SERVER_SYNC_FILE):
    # Step 1 : Read data from database 
    current_time = get_utc()
    
    global id_upload_chanel
    global data_sent_server
    global status_sync
    global count
    global number_file 
    global multifile
    global time_retry
    global vals
    
    global QUERY_SYNC_SERVER
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_DATABASE
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    global QUERY_GET_THE_KEY
    global QUERY_SELECT_SERIAL_NUMBER
    global QUERY_SELECT_URL
    
    id_device_fr_sys = id_upload_chanel[1]
    data_sync_server = []
    template_names  = []
    data_sent_server_list = []
    data_sync_dict = []
    devices = []
    file = []
    files = []
    name_serial_device = ""
    url = ""
    # array_file = []
    # array_files = []
    data_insert_many_temp = []
    data_insert_many = []
    val = []
    global json_data 
    global json_datas
    file = {}
    json_datas = {}
    
    global number_device
    global array_file
    global array_files
    result1 =[]
    result2 =[]
    result3 =[]
    by_pass = 0 

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
        
    result1 = await MySQL_Select_v1(QUERY_NUMER_FILE)
    number_file = result1[0]["remaining_files"]
    
    result2 = await MySQL_Select_v1(QUERY_SELECT_SERIAL_NUMBER)
    name_serial_device = result2[0]["serial_number_port"] 
    
    result3 = MySQL_Select(QUERY_SELECT_URL,(id_device_fr_sys,))
    url = result3[0]["uploadurl"] 
    
    if multifile is False :
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
                    with open(device.source, 'r') as file:
                        device.file_content = file.read()
                        device.file_size = os.path.getsize(device.source)
                        if device.file_size > 0 :
                            device.data_file = {'file_name': device.file_name, 'file_content': device.file_content}
                        else :
                            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
                                upErr_Database(device.time_id,device.id_device)
                                by_pass = 1 
                            else:
                                pass
                else:
                    upErr_Database(device.time_id,device.id_device)
                    by_pass = 1    
                if os.path.exists(device.source):     
                    # sent 1 file to server  
                    # files = {'file': (device.file_name, open(device.source, 'rb'))}
                    headers = {
                        'SERIALNUMBER': '1',
                        'MODBUSDEVICE': '1',
                        'MODBUSPORT': '1',
                        'MODE': '1'
                    }

                    files = [('file', (device.file_name, open(device.source, 'rb'))),]
                    
                    print("="*40, "filename", "="*40)
                    print(f"Name file: {device.file_name}")
                    
                    
                    
                    

                else:
                    upErr_Database(device.time_id,device.id_device)
                        
                # files = [('files', (device.file_name, open(device.source, 'rb'), 'text/plain')),]
                if device.data_file : 
                    array_file = device.file_content.split(',')
                    # Tạo đối tượng JSON dựa trên mảng dữ liệu
                    if name_serial_device :
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
                    else :
                        pass

                template_names = MySQL_Select(QUERY_GET_THE_KEY, (device.id_device,))

                # Vòng lặp để thay đổi key
                if template_names : 
                    for i in range(4, len(array_file)):
                        if i - 4 < len(template_names):
                            key = template_names[i-4]
                            value = array_file[i] if array_file[i] else None
                            json_data["datas"][key['template_name']] = value
                        else:
                            print(f"Không đủ phần tử trong template_names cho chỉ số {i}")
                print("="*40, "Json Sent Sever", "="*40)
                print(f"Json: {json_data}")
                print("="*40, "url", "="*40)
                print(f"URL_SERVER_SYNC: {url}")

                try:
                    if json_data or files:
                        response = requests.post(url, json=json_data)  # Sử dụng tham số "json" để tự động chuyển đổi dữ liệu thành JSON
                        # response = requests.post(url, files=files)
                        if response.status_code == 200:
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
            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
                upErr_Database(device.time_id,device.id_device)
            pass
    else :# There are a lot of files 
        try :
            if id_device_fr_sys :
                data_sync_server = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,id_device_fr_sys,))
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
                            
                    array_file = devices[i].file_content.split(',')
                    
                    # Gom file lại gửi len server 1 lần
                    if os.path.exists(devices[i].source):
                        file = ('files', ( devices[i].file_name, open( devices[i].source, 'rb'), 'text/plain'))
                        files.append(file)
                    else:
                        upErr_Database(devices[i].time_id,devices[i].id_device)

                    # Thu thập dữ liệu sau khi gửi data thành công thì update vào trong database 
                    data_insert_many_temp = (current_time,devices[i].time_id ,id_device_fr_sys , devices[i].id_device)
                    data_insert_many.append(data_insert_many_temp)
                    # Thu thập thông tin khi xảy ra lỗi thì update số lần lỗi vào database
                    val = (count,devices[i].time_id ,id_device_fr_sys ,devices[i].id_device)
                    if count > 0 :
                        vals.append(val)
                    # Tạo đối tượng JSON dựa trên mảng dữ liệu từ thiết bị hiện tại
                    if name_serial_device : 
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
                    else :
                        pass

                    template_names = MySQL_Select(QUERY_GET_THE_KEY, (devices[i].id_device,))

                    # Vòng lặp để thay đổi key
                    for i in range(4, len(array_file)):
                        if i - 4 < len(template_names):
                            key = template_names[i-4]
                            value = array_file[i] if array_file[i] else None
                            json_data_total["datas"][key['template_name']] = value
                        else:
                            # print(f"Không đủ phần tử trong template_names cho chỉ số {i}")
                            pass
                    print("="*40, "Json Sent Sever", "="*40)
                    print(f"Json: {json_data_total}")
                    
                    try:
                        if json_data_total:
                            response = requests.post(url, json=json_data_total)  # Sử dụng tham số "json" để tự động chuyển đổi dữ liệu thành JSON
                            # response = requests.post(url, files = files)
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
    global number_file 
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
    path = []
    paths = []
    data_insert_many_temp = []
    data_insert_many = []
    val = []
    
    
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

    result1 = await MySQL_Select_v1(QUERY_NUMER_FILE)
    number_file = result1[0]["remaining_files"]
        
    if multifile is False :
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
                            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
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
            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
                upErr_Database(device.time_id,device.id_device)
            pass
    else :
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
                        
                    # print("path " ,devices.source[i] )
                    # path = (devices.source[i])
                    # paths.append(path)
                    # all_contents = [] 
                    # for item in paths:
                    #     with open(item, "r") as file:
                    #         content = file.read().strip()
                    #         all_contents.append(content)
                    # count_FTP_Server += 1
                    # new_file_path = f"D:/library/NEXTWWAVE/LogFile/merged_{count_FTP_Server}.txt"
                    # with open(new_file_path, "w+") as new_file:
                    #     new_file.write("\n".join(all_contents))
                        
                    # print("Nội dung đã được ghi vào file mới:", new_file_path)
        #             try:
        #                 if len(data_sent_server_list)==10 and by_pass == 0 :
        #                     isUploadSuccess = uploadFileToFtp(new_file_path,FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD)
        #                     if isUploadSuccess == True :
        #                         # Step 3 : Updata sync server with database
        #                         MySQL_Update_v2(QUERY_UPDATE_DATABASE,data_insert_many)
        #                         status_sync = 1
        #                         count = 0 
        #                     else:
        #                         Executeup_NumberRetry_Database_Multies(time_retry)
        #                         status_sync = 0
        #             except Exception as e:
        #                 Executeup_NumberRetry_Database_Multies(time_retry)
        #                 status_sync = 0 
        #                 print('An exception occurred',e)
        # else : 
        #     if len(devices[i].time_id)> 0 and len(str(devices[i].id_device))> 0 :
        #         upErr_Database(devices[i].time_id,devices[i].id_device)
        #     else :
        #         pass

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
    global QUERY_ALL_DEVICES
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
    global QUERY_GET_THE_KEY
    global QUERY_UPDATE_SERIAL_NUMBER
    global QUERY_SELECT_SERIAL_NUMBER
    global QUERY_SELECT_URL
    
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
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
        QUERY_GET_THE_KEY = result_mybatis["QUERY_GET_THE_KEY"]
        QUERY_UPDATE_SERIAL_NUMBER = result_mybatis["QUERY_UPDATE_SERIAL_NUMBER"]
        QUERY_SELECT_SERIAL_NUMBER = result_mybatis["QUERY_SELECT_SERIAL_NUMBER"]
        QUERY_SELECT_URL = result_mybatis["QUERY_SELECT_URL"]
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_GETDATA_SERVER or not QUERY_ALL_DEVICES or not QUERY_SYNC_SERVER or not QUERY_UPDATE_DATABASE or not QUERY_TIME_SYNC_DATA or not QUERY_UPDATE_ERR_DATABASE or not QUERY_TIME_RETRY or not QUERY_UPDATE_NUMBERRETRY or not QUERY_NUMER_FILE or not QUERY_SYNC_MULTIFILE_SERVER or not QUERY_SYNC_ERROR_MQTT or not QUERY_GET_THE_KEY or not QUERY_UPDATE_SERIAL_NUMBER or not QUERY_SELECT_SERIAL_NUMBER or not QUERY_SELECT_URL:
        print("Error not found data in file mybatis")
        return -1
    try: 
        result1 = await MySQL_Select_v1(QUERY_NUMER_FILE)
        number_file = result1[0]["remaining_files"]
        if number_file <= 2000 :
            multifile = False 
        else :
            multifile = True 
        result = await MySQL_Select_v1(QUERY_TIME_RETRY)
        time_retry = result[0]["time_log_data_server"]
        result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
        time_data_server = await MySQL_Select_v1(QUERY_GETDATA_SERVER)
        id_device_fr_sys = id_upload_chanel[1]
        time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
        for item in time_sync_data:
            type_file = item["type_protocol"]
    except Exception as e:
            print('An exception occurred',e)
    if not result_all or not time_data_server :
        print("Error not found data in Database")
        return -1
    
    serial_number = get_serial_number_windows()
    if serial_number :
        MySQL_Update_V1(QUERY_UPDATE_SERIAL_NUMBER,(serial_number,))
    else :
        pass
        
    if result_all and time_data_server :
        time_sentdata = time_data_server[0]["time_log_data_server"]
        time_sentdata = 100 # test 
        if time_sentdata and count <= 1 and type_file == "URL":
                if 0 <= time_sentdata <= 24:
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'cron', hour = time_sentdata,  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 95 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'interval', hours = "12",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 96 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'interval', hours = "8",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 97 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'interval', minutes = f"{time_sentdata}",  args=[URL_SERVER_SYNC])
                    scheduler.start()
                elif time_sentdata == 98 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'interval', minutes = "15",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 99 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'interval', hours = "1",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 100 : # test cron 
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerURL_Database, 'cron', second = "*/10",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
        if time_sentdata and count <= 1 and type_file == "FTP":
                if 0 <= time_sentdata <= 24:
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'cron', hour = time_sentdata,  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 95 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = "12",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 96 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = "8",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 97 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'interval', minutes = f"{time_sentdata}",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 98 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'interval', minutes = "15",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 99 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'interval', hours = "1",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                elif time_sentdata == 100 : # test cron 
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_ServerFTP_Database, 'cron', second = "*/10",  args=[FTPSERVER_HOSTNAME, FTPSERVER_PORT, FTPSERVER_USERNAME, FTPSERVER_PASSWORD])
                    scheduler.start()
                
    scheduler = AsyncIOScheduler()
    scheduler.add_job(colectDatatoPushMQTT, 'interval', seconds = 3 , args=[MQTT_BROKER,
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
    

# song phan gui url 1 file va nhieu file , mat server , mat connect sql , mat connect mqtt , ok 
# song phan gui url 1 json va nhieu json , mat server , mat connect sql , mat connect mqtt , ok 
# no co 1 loi la ket qua sql bi day se khong chay duoc phai chay cau lenh sql : UPDATE sync_data SET synced = DEFAULT, updatetime = DEFAULT , error = DEFAULT , number_of_time_retry = DEFAULT;



