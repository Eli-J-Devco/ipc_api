import asyncio
import datetime
import json
import logging
import os
import sys

import mqttools
import mybatis_mapper2sql
import paho.mqtt.publish as publish

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import *
from libMySQL import *

arr = sys.argv
id_upload_chanel = arr
DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
DATABASE_PORT = Config.DATABASE_PORT
DATABASE_USERNAME = Config.DATABASE_USERNAME
DATABASE_PASSWORD = Config.DATABASE_PASSWORD
DATABASE_NAME = Config.DATABASE_NAME
URL_SERVER_SYNC = Config.URL_SERVER_SYNC
URL_SERVER_SYNC_FILE = Config.URL_SERVER_SYNC_FILE

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

data_sent_server = {}
data_sent_server_list = []
json_data = {}
json_data_list = []
data = 0
status_sync = 0 
count = 0
sync_immediately = 0 
flag_sync_immediately = False 
flag_end_update = False
count =0 
number_file = 0
multifile = False

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
                await sync_Server_Database(URL_SERVER_SYNC)
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
    
    data_sent_server_mqtt = []
    data_sent_server_list_mqtt = []
    data_sync_server_mqtt = []
    data_sync_dict = []
    
    sql_id = ""
    file_name = ""
    number_time_retry = ""
    sql_id_str = ""
    device_name = ""
    error = ""
    result_error = ""
    status = False
    sql_id1 = ""
    file_name1 = ""
    number_time_retry1 = ""
    sql_id_str1 = ""
    device_name1 = ""
    error1 = ""
    result_error1 = ""
    status1 = False
    sql_id2 = ""
    file_name2 = ""
    number_time_retry2 = ""
    sql_id_str2 = ""
    device_name2 = ""
    error2 = ""
    result_error2 = ""
    status2 = False
    sql_id3 = ""
    file_name3 = ""
    number_time_retry3 = ""
    sql_id_str3 = ""
    device_name3 = ""
    error3 = ""
    result_error3 = ""
    status3 = False
    sql_id4 = ""
    file_name4 = ""
    number_time_retry4 = ""
    sql_id_str4 = ""
    device_name4 = ""
    error4 = ""
    result_error4 = ""
    status4 = False
    sql_id5 = ""
    file_name5 = ""
    number_time_retry5 = ""
    sql_id_str5 = ""
    device_name5 = ""
    error5 = ""
    result_error5 = ""
    status5 = False
    sql_id6 = ""
    file_name6 = ""
    number_time_retry6 = ""
    sql_id_str6 = ""
    device_name6 = ""
    error6 = ""
    result_error6 = ""
    status6 = False
    sql_id7 = ""
    file_name7 = ""
    number_time_retry7 = ""
    sql_id_str7 = ""
    device_name7 = ""
    error7 = ""
    result_error7 = ""
    status7 = False
    sql_id8 = ""
    file_name8 = ""
    number_time_retry8 = ""
    sql_id_str8 = ""
    device_name8 = ""
    error8 = ""
    result_error8 = ""
    status8 = False
    sql_id9 = ""
    file_name9 = ""
    number_time_retry9 = ""
    sql_id_str9 = ""
    device_name9 = ""
    error9 = ""
    result_error9 = ""
    status9 = False
    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 
    id_device_fr_sys = id_upload_chanel[1]
    time_sync_data = MySQL_Select(QUERY_TIME_SYNC_DATA,(id_device_fr_sys,))
    for item in time_sync_data:
        type_file = item["type_protocol"]
    try :
        if multifile is False :
            data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_SERVER,(id_device_fr_sys,))
        elif multifile is True :
            data_sync_server_mqtt = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,))
            if data_sync_server_mqtt :
                for item in data_sync_server_mqtt :
                    data_sync_dict = item       
                    id_device = data_sync_dict['id_device']
                    filename = data_sync_dict['filename']  
                    number_time_retry = data_sync_dict['number_of_time_retry']
                    error = data_sync_dict['error']
                    
                    data_sent_server_mqtt = { "id_device": id_device , "filename": filename,"number_of_time_retry": number_time_retry , "error":error}
                    data_sent_server_list_mqtt.append(data_sent_server_mqtt)
                    
    except Exception as e: 
        print('An exception occurred',e)
    if multifile is False :
        if data_sync_server_mqtt :
            data_sync_dict = data_sync_server_mqtt[0]
            if 'id_device' not in data_sync_dict:
                return -1 
            if 'filename' not in data_sync_dict:
                return -1 
            if 'number_of_time_retry' not in data_sync_dict:
                return -1 
            
            sql_id = data_sync_dict['id_device']        
            file_name = data_sync_dict['filename']
            number_time_retry = data_sync_dict['number_of_time_retry']
            # File creation time 
            sql_id_str = str(sql_id)
            device_name = [item['name'] for item in result_all if item['id'] == sql_id][0]
            
            current_time = get_utc()
            ts_timestamp = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
            datetime_obj = datetime.datetime.fromtimestamp(ts_timestamp)
            date_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            if status_sync == 1 : 
                status = "Success"
            else :
                status = "Fault"
            data_mqtt={
                "ID_DEVICE":sql_id_str,
                "FILE_NAME": file_name,
                "Timestamp": date_str,
                "Status_file_toserver": status,
                "number_time_retry": number_time_retry, 
            }
            
            pushMQTT(host,
                    port,
                    topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str+"|"+device_name,
                    username,
                    password,
                    data_mqtt)
    else : 
        if data_sent_server_list_mqtt :
            sql_id = data_sent_server_list_mqtt[0]['id_device']        
            file_name = data_sent_server_list_mqtt[0]['filename']
            number_time_retry = data_sent_server_list_mqtt[0]['number_of_time_retry']
            result_error = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name))
            error = result_error[0]["error"]

            sql_id1 = data_sent_server_list_mqtt[1]['id_device']        
            file_name1 = data_sent_server_list_mqtt[1]['filename']
            number_time_retry1 = data_sent_server_list_mqtt[1]['number_of_time_retry']
            result_error1 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name1))
            error1 = result_error1[0]["error"]
            
            sql_id2 = data_sent_server_list_mqtt[2]['id_device']        
            file_name2 = data_sent_server_list_mqtt[2]['filename']
            number_time_retry2 = data_sent_server_list_mqtt[2]['number_of_time_retry']
            result_error2 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name2))
            error2 = result_error2[0]["error"]
            
            sql_id3 = data_sent_server_list_mqtt[3]['id_device']        
            file_name3 = data_sent_server_list_mqtt[3]['filename']
            number_time_retry3 = data_sent_server_list_mqtt[3]['number_of_time_retry']
            result_error3 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name3))
            error3 = result_error3[0]["error"]
            
            sql_id4 = data_sent_server_list_mqtt[4]['id_device']        
            file_name4 = data_sent_server_list_mqtt[4]['filename']
            number_time_retry4 = data_sent_server_list_mqtt[4]['number_of_time_retry']
            result_error4 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name4))
            error4 = result_error4[0]["error"]
            
            sql_id5 = data_sent_server_list_mqtt[5]['id_device']        
            file_name5 = data_sent_server_list_mqtt[5]['filename']
            number_time_retry5 = data_sent_server_list_mqtt[5]['number_of_time_retry']
            result_error5 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name5))
            error5 = result_error5[0]["error"]
            
            sql_id6 = data_sent_server_list_mqtt[6]['id_device']        
            file_name6 = data_sent_server_list_mqtt[6]['filename']
            number_time_retry6 = data_sent_server_list_mqtt[6]['number_of_time_retry']
            result_error6 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name6))
            error6 = result_error6[0]["error"]
            
            sql_id7 = data_sent_server_list_mqtt[7]['id_device']        
            file_name7 = data_sent_server_list_mqtt[7]['filename']
            number_time_retry7 = data_sent_server_list_mqtt[7]['number_of_time_retry']
            result_error7 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name7))
            error7 = result_error7[0]["error"]
            
            sql_id8 = data_sent_server_list_mqtt[8]['id_device']        
            file_name8 = data_sent_server_list_mqtt[8]['filename']
            number_time_retry8 = data_sent_server_list_mqtt[8]['number_of_time_retry']
            result_error8 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name8))
            error8 = result_error8[0]["error"]
            
            sql_id9 = data_sent_server_list_mqtt[9]['id_device']        
            file_name9 = data_sent_server_list_mqtt[9]['filename']
            number_time_retry9 = data_sent_server_list_mqtt[9]['number_of_time_retry']
            result_error9 = MySQL_Select(QUERY_SYNC_ERROR_MQTT,(id_device_fr_sys,file_name9))
            error9 = result_error9[0]["error"]
            
            # File creation time 
            sql_id_str = str(sql_id)
            device_name = [item['name'] for item in result_all if item['id'] == sql_id][0]
            
            sql_id_str1 = str(sql_id1)
            device_name1 = [item['name'] for item in result_all if item['id'] == sql_id1][0]
            
            sql_id_str2 = str(sql_id2)
            device_name2 = [item['name'] for item in result_all if item['id'] == sql_id2][0]
            
            sql_id_str3 = str(sql_id3)
            device_name3 = [item['name'] for item in result_all if item['id'] == sql_id3][0]
            
            sql_id_str4 = str(sql_id4)
            device_name4 = [item['name'] for item in result_all if item['id'] == sql_id4][0]
            
            sql_id_str5 = str(sql_id5)
            device_name5 = [item['name'] for item in result_all if item['id'] == sql_id5][0]
            
            sql_id_str6 = str(sql_id6)
            device_name6 = [item['name'] for item in result_all if item['id'] == sql_id6][0]
            
            sql_id_str7 = str(sql_id7)
            device_name7 = [item['name'] for item in result_all if item['id'] == sql_id7][0]
            
            sql_id_str8 = str(sql_id8)
            device_name8 = [item['name'] for item in result_all if item['id'] == sql_id8][0]
            
            sql_id_str9 = str(sql_id9)
            device_name9 = [item['name'] for item in result_all if item['id'] == sql_id9][0]
            
            current_time = get_utc()
            ts_timestamp = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S").timestamp()
            datetime_obj = datetime.datetime.fromtimestamp(ts_timestamp)
            date_str = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
            
            if status_sync == 1 :
                if error != 1 : 
                    status = "Success"
                else :
                    status = "Fault"
                if error1 != 1 : 
                    status1 = "Success"
                else :
                    status1 = "Fault"
                if error2 != 1 : 
                    status2 = "Success"
                else :
                    status2 = "Fault"
                if error3 != 1 : 
                    status3 = "Success"
                else :
                    status3 = "Fault"
                if error4 != 1 : 
                    status4 = "Success"
                else :
                    status4 = "Fault"
                if error5 != 1 : 
                    status5 = "Success"
                else :
                    status5 = "Fault"
                if error6 != 1 : 
                    status6 = "Success"
                else :
                    status6 = "Fault"
                if error7 != 1 : 
                    status7 = "Success"
                else :
                    status7 = "Fault"
                if error8 != 1 : 
                    status8 = "Success"
                else :
                    status8 = "Fault"
                if error9 != 1 : 
                    status9 = "Success"
                else :
                    status9 = "Fault"
            
            data_mqtt={"ID_DEVICE":sql_id_str,"FILE_NAME": file_name,"Timestamp": date_str,"Status_file_toserver": status,"number_time_retry": number_time_retry, }
            data_mqtt1={"ID_DEVICE":sql_id_str1,"FILE_NAME": file_name1,"Timestamp": date_str,"Status_file_toserver": status1,"number_time_retry": number_time_retry1, }
            data_mqtt2={"ID_DEVICE":sql_id_str2,"FILE_NAME": file_name2,"Timestamp": date_str,"Status_file_toserver": status2,"number_time_retry": number_time_retry2, }
            data_mqtt3={"ID_DEVICE":sql_id_str3,"FILE_NAME": file_name3,"Timestamp": date_str,"Status_file_toserver": status3,"number_time_retry": number_time_retry3, }
            data_mqtt4={"ID_DEVICE":sql_id_str4,"FILE_NAME": file_name4,"Timestamp": date_str,"Status_file_toserver": status4,"number_time_retry": number_time_retry4, }
            data_mqtt5={"ID_DEVICE":sql_id_str5,"FILE_NAME": file_name5,"Timestamp": date_str,"Status_file_toserver": status5,"number_time_retry": number_time_retry5, }
            data_mqtt6={"ID_DEVICE":sql_id_str6,"FILE_NAME": file_name6,"Timestamp": date_str,"Status_file_toserver": status6,"number_time_retry": number_time_retry6, }
            data_mqtt7={"ID_DEVICE":sql_id_str7,"FILE_NAME": file_name7,"Timestamp": date_str,"Status_file_toserver": status7,"number_time_retry": number_time_retry7, }
            data_mqtt8={"ID_DEVICE":sql_id_str8,"FILE_NAME": file_name8,"Timestamp": date_str,"Status_file_toserver": status8,"number_time_retry": number_time_retry8, }
            data_mqtt9={"ID_DEVICE":sql_id_str9,"FILE_NAME": file_name9,"Timestamp": date_str,"Status_file_toserver": status9,"number_time_retry": number_time_retry9, }
            
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str+"|"+device_name,username,password,data_mqtt)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str1+"|"+device_name1,username,password,data_mqtt1)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str2+"|"+device_name2,username,password,data_mqtt2)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str3+"|"+device_name3,username,password,data_mqtt3)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str4+"|"+device_name4,username,password,data_mqtt4)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str5+"|"+device_name5,username,password,data_mqtt5)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str6+"|"+device_name6,username,password,data_mqtt6)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str7+"|"+device_name7,username,password,data_mqtt7)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str8+"|"+device_name8,username,password,data_mqtt8)
            pushMQTT(host,port,topic + f"/Channel{id_device_fr_sys}/{type_file}/"+sql_id_str9+"|"+device_name9,username,password,data_mqtt9)
        
# Describe sync_Server_Database
# /**
# 	 * @description read data from database , send data to server , update data sent in database
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
async def sync_Server_Database(URL_SERVER_SYNC, URL_SERVER_SYNC_FILE):
    # Step 1 : Read data from database 
    current_time = get_utc()
    
    global id_upload_chanel
    global data_sent_server
    global status_sync
    global count
    global number_file 
    global multifile
    
    global QUERY_SYNC_SERVER
    global QUERY_TIME_RETRY
    global QUERY_UPDATE_DATABASE
    global QUERY_NUMER_FILE
    global QUERY_SYNC_MULTIFILE_SERVER
    
    id_device_fr_sys = id_upload_chanel[1]
    data_sync_server = []
    data_sent_server_list = []
    data_sync_dict = []
    id = []
    id_device =[]
    modbusdevice =[]
    data =[]
    
    json_data = {}
    file1 = {}
    file2 = {}
    file3 = {}
    file4 = {}
    file5 = {}
    file6 = {}
    file7 = {}
    file8 = {}
    file9 = {}
    file = {}
    
    
    Time = ""
    Id_device = ""
    source = ""
    filename = ""
    file_content =""
    data_file = ""
    Time1 = ""
    Id_device1 = ""
    source1 = ""
    filename1 = ""
    file_content1 =""
    data_file1 = ""
    Time2 = ""
    Id_device2 = ""
    source2 = ""
    filename2 = ""
    file_content2 =""
    data_file2 = ""
    Time3 = ""
    Id_device3 = ""
    source3 = ""
    filename3 = ""
    file_content3 =""
    data_file3 = ""
    Time4 = ""
    Id_device4 = ""
    source4 = ""
    filename4 = ""
    file_content4 =""
    data_file4 = ""
    Time5 = ""
    Id_device5 = ""
    source5 = ""
    filename5 = ""
    file_content5 =""
    data_file5 = ""
    Time6 = ""
    Id_device6 = ""
    source6 = ""
    filename6 = ""
    file_content6 =""
    data_file6 = ""
    Time7 = ""
    Id_device7 = ""
    source7 = ""
    filename7 = ""
    file_content7 =""
    data_file7 = ""
    Time8 = ""
    Id_device8 = ""
    source8 = ""
    filename8 = ""
    file_content8 =""
    data_file8 = ""
    Time9 = ""
    Id_device9 = ""
    source9 = ""
    filename9 = ""
    file_content9 =""
    data_file9 = ""
    by_pass = 0 

    result = await MySQL_Select_v1(QUERY_TIME_RETRY)
    time_retry = result[0]["time_log_data_server"]
    
    result1 = await MySQL_Select_v1(QUERY_NUMER_FILE)
    number_file = result1[0]["remaining_files"]
    
    if number_file <= 2000 :
        multifile = False
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
                    
                    id = data_sync_dict['id']        
                    id_device = data_sync_dict['id_device']
                    modbusdevice = data_sync_dict['modbusdevice']
                    data = data_sync_dict['data']   
                    filename = data_sync_dict['filename']  
                    source = data_sync_dict['source']
                    data_sql = data_sync_dict['data']
                    
                    data_sent_server = {"id": id, "id_device": id_device, "modbusdevice": modbusdevice, "data": data , "filename": filename,"source": source,"data_sql": data_sql}
                    if len(str(modbusdevice)) == 0 or len(data) == 0 :
                        upErr_Database(id,id_device) 
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
            if 'data' not in data_sent_server:
                return -1

            if (len(str(data_sent_server['id_device'])) > 0
                and len(str(data_sent_server['modbusdevice'])) > 0
                and len(data_sent_server["data"]) > 0):

                if isinstance(data_sent_server['id'], datetime.datetime):
                    data_sent_server['id'] = data_sent_server['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                data_sent_server["data"] = data_sent_server["data"].strip("'") 
                
                Time = data_sent_server['id']
                Id_device = data_sent_server["id_device"]
                filename = data_sent_server["filename"]
                source = data_sent_server["source"]
                data_sql = data_sent_server["data_sql"]
                
                if filename :
                    with open(source, 'r') as file:
                        file_content = file.read()
                        if len(file_content) > 0 and file_content == data_sql:
                            data_file = {'file_name': filename, 'file_content': file_content}
                        else :
                            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
                                upErr_Database(Time,Id_device)
                                by_pass = 1 
                            
                if data_file : 
                    json_data = {
                            "id": data_sent_server['id'],
                            "id_device": data_sent_server["id_device"],
                            "modbusdevice": data_sent_server["modbusdevice"],
                            "data": data_sent_server["data"],
                            "data_file" :data_file 
                            }
                    files = {'file': (filename, open(source, 'rb'))}
                try:
                    if data_sent_server and by_pass == 0 :
                        response = requests.post(URL_SERVER_SYNC, data = json_data , files = files)
                        if response.status_code == 200:
                            # Step 3 : update data error in database
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time ,id_device_fr_sys , Id_device))
                            print(response.json())
                            status_sync = 1
                            count = 0 
                        else:
                            print(response.json())
                            status_sync = 0
                            Executeup_NumberRetry_Database(time_retry,Time,Id_device)
                except Exception as e:
                    status_sync = 0 
                    Executeup_NumberRetry_Database(time_retry,Time,Id_device)
                    print('An exception occurred',e)
        else : 
            if len(data_sent_server["id"])> 0 and len(str(data_sent_server["id_device"]))> 0 :
                upErr_Database(Time,Id_device)
    else :# There are a lot of files 
        multifile = True
        try :
            data_sync_server = MySQL_Select(QUERY_SYNC_MULTIFILE_SERVER,(id_device_fr_sys,))
            if data_sync_server :
                for item in data_sync_server :
                    data_sync_dict = item 
                    id = data_sync_dict['id']        
                    id_device = data_sync_dict['id_device']
                    modbusdevice = data_sync_dict['modbusdevice']
                    data = data_sync_dict['data']   
                    filename = data_sync_dict['filename']  
                    source = data_sync_dict['source']
                    data_sql = data_sync_dict['data']
                    
                    data_sent_server = {"id": id, "id_device": id_device, "modbusdevice": modbusdevice, "data": data , "filename": filename,"source": source,"data_sql": data_sql}
                    data_sent_server_list.append(data_sent_server)
                    
                if len(str(data_sent_server_list[0]["modbusdevice"])) == 0 or len(data_sent_server_list[0]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[0]["id"],data_sent_server_list[0]["id_device"]) 
                    
                if len(str(data_sent_server_list[1]["modbusdevice"])) == 0 or len(data_sent_server_list[1]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[1]["id"],data_sent_server_list[1]["id_device"]) 
                    
                if len(str(data_sent_server_list[2]["modbusdevice"])) == 0 or len(data_sent_server_list[2]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[2]["id"],data_sent_server_list[2]["id_device"]) 
                    
                if len(str(data_sent_server_list[3]["modbusdevice"])) == 0 or len(data_sent_server_list[3]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[3]["id"],data_sent_server_list[3]["id_device"]) 
                    
                if len(str(data_sent_server_list[4]["modbusdevice"])) == 0 or len(data_sent_server_list[4]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[4]["id"],data_sent_server_list[4]["id_device"]) 
                    
                if len(str(data_sent_server_list[5]["modbusdevice"])) == 0 or len(data_sent_server_list[5]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[5]["id"],data_sent_server_list[5]["id_device"]) 
                    
                if len(str(data_sent_server_list[6]["modbusdevice"])) == 0 or len(data_sent_server_list[6]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[6]["id"],data_sent_server_list[6]["id_device"]) 
                    
                if len(str(data_sent_server_list[7]["modbusdevice"])) == 0 or len(data_sent_server_list[7]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[7]["id"],data_sent_server_list[7]["id_device"]) 
                    
                if len(str(data_sent_server_list[8]["modbusdevice"])) == 0 or len(data_sent_server_list[8]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[8]["id"],data_sent_server_list[8]["id_device"]) 
                    
                if len(str(data_sent_server_list[9]["modbusdevice"])) == 0 or len(data_sent_server_list[9]["data"]) == 0 :
                    upErr_Database(data_sent_server_list[9]["id"],data_sent_server_list[9]["id_device"]) 
                
        except Exception as e: 
            print('An exception occurred',e)
        else :
            pass
            data_sent_server_list = data_sent_server_list
        #Step 2 : Sent data to server 
        if data_sent_server_list : 
            if (len(data_sent_server_list) == 10 and len(str(data_sent_server_list[0]['id_device'])) > 0 and len(str(data_sent_server_list[1]['id_device'])) > 0 and len(str(data_sent_server_list[2]['id_device'])) > 0 and len(str(data_sent_server_list[3]['id_device'])) > 0 and len(str(data_sent_server_list[4]['id_device'])) > 0 and len(str(data_sent_server_list[5]['id_device'])) > 0 and len(str(data_sent_server_list[6]['id_device'])) > 0 and len(str(data_sent_server_list[7]['id_device'])) > 0 and len(str(data_sent_server_list[8]['id_device'])) > 0 and len(str(data_sent_server_list[9]['id_device'])) > 0 
                and len(str(data_sent_server_list[0]['modbusdevice'])) > 0 and len(str(data_sent_server_list[1]['modbusdevice'])) > 0 and len(str(data_sent_server_list[2]['modbusdevice'])) > 0 and len(str(data_sent_server_list[3]['modbusdevice'])) > 0 and len(str(data_sent_server_list[4]['modbusdevice'])) > 0 and len(str(data_sent_server_list[5]['modbusdevice'])) > 0 and len(str(data_sent_server_list[6]['modbusdevice'])) > 0 and len(str(data_sent_server_list[7]['modbusdevice'])) > 0 and len(str(data_sent_server_list[8]['modbusdevice'])) > 0 and len(str(data_sent_server_list[9]['modbusdevice'])) > 0 
                and len(data_sent_server_list[0]["data"]) > 0 and len(data_sent_server_list[1]["data"]) > 0 and len(data_sent_server_list[2]["data"]) > 0 and len(data_sent_server_list[3]["data"]) > 0 and len(data_sent_server_list[4]["data"]) > 0 and len(data_sent_server_list[5]["data"]) > 0 and len(data_sent_server_list[6]["data"]) > 0 and len(data_sent_server_list[7]["data"]) > 0 and len(data_sent_server_list[8]["data"]) > 0 and len(data_sent_server_list[9]["data"]) > 0 ):
                
                if isinstance(data_sent_server_list[0]['id'], datetime.datetime):
                    data_sent_server_list[0]['id'] = data_sent_server_list[0]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[1]['id'], datetime.datetime):
                    data_sent_server_list[1]['id'] = data_sent_server_list[1]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[2]['id'], datetime.datetime):
                    data_sent_server_list[2]['id'] = data_sent_server_list[2]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[3]['id'], datetime.datetime):
                    data_sent_server_list[3]['id'] = data_sent_server_list[3]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[4]['id'], datetime.datetime):
                    data_sent_server_list[4]['id'] = data_sent_server_list[4]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[5]['id'], datetime.datetime):
                    data_sent_server_list[5]['id'] = data_sent_server_list[5]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[6]['id'], datetime.datetime):
                    data_sent_server_list[6]['id'] = data_sent_server_list[6]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[7]['id'], datetime.datetime):
                    data_sent_server_list[7]['id'] = data_sent_server_list[7]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[8]['id'], datetime.datetime):
                    data_sent_server_list[8]['id'] = data_sent_server_list[8]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                if isinstance(data_sent_server_list[9]['id'], datetime.datetime):
                    data_sent_server_list[9]['id'] = data_sent_server_list[9]['id'].strftime('%Y-%m-%d %H:%M:%S')
                else:
                    pass
                
                data_sent_server_list[0]["data"] = data_sent_server_list[0]["data"].strip("'") 
                data_sent_server_list[1]["data"] = data_sent_server_list[1]["data"].strip("'") 
                data_sent_server_list[2]["data"] = data_sent_server_list[2]["data"].strip("'") 
                data_sent_server_list[3]["data"] = data_sent_server_list[3]["data"].strip("'") 
                data_sent_server_list[4]["data"] = data_sent_server_list[4]["data"].strip("'") 
                data_sent_server_list[5]["data"] = data_sent_server_list[5]["data"].strip("'") 
                data_sent_server_list[6]["data"] = data_sent_server_list[6]["data"].strip("'") 
                data_sent_server_list[7]["data"] = data_sent_server_list[7]["data"].strip("'") 
                data_sent_server_list[8]["data"] = data_sent_server_list[8]["data"].strip("'") 
                data_sent_server_list[9]["data"] = data_sent_server_list[9]["data"].strip("'") 
                
                Time = data_sent_server_list[0]["id"]
                Time1 = data_sent_server_list[1]["id"]
                Time2 = data_sent_server_list[2]["id"]
                Time3 = data_sent_server_list[3]["id"]
                Time4 = data_sent_server_list[4]["id"]
                Time5 = data_sent_server_list[5]["id"]
                Time6 = data_sent_server_list[6]["id"]
                Time7 = data_sent_server_list[7]["id"]
                Time8 = data_sent_server_list[8]["id"]
                Time9 = data_sent_server_list[9]["id"]
                
                Id_device = data_sent_server_list[0]["id_device"]
                Id_device1 = data_sent_server_list[1]["id_device"]
                Id_device2 = data_sent_server_list[2]["id_device"]
                Id_device3 = data_sent_server_list[3]["id_device"]
                Id_device4 = data_sent_server_list[4]["id_device"]
                Id_device5 = data_sent_server_list[5]["id_device"]
                Id_device6 = data_sent_server_list[6]["id_device"]
                Id_device7 = data_sent_server_list[7]["id_device"]
                Id_device8 = data_sent_server_list[8]["id_device"]
                Id_device9 = data_sent_server_list[9]["id_device"]
                
                filename = data_sent_server_list[0]["filename"]
                filename1 = data_sent_server_list[1]["filename"]
                filename2 = data_sent_server_list[2]["filename"]
                filename3 = data_sent_server_list[3]["filename"]
                filename4 = data_sent_server_list[4]["filename"]
                filename5 = data_sent_server_list[5]["filename"]
                filename6 = data_sent_server_list[6]["filename"]
                filename7 = data_sent_server_list[7]["filename"]
                filename8 = data_sent_server_list[8]["filename"]
                filename9 = data_sent_server_list[9]["filename"]
                
                source = data_sent_server_list[0]["source"]
                source1 = data_sent_server_list[1]["source"]
                source2 = data_sent_server_list[2]["source"]
                source3 = data_sent_server_list[3]["source"]
                source4 = data_sent_server_list[4]["source"]
                source5 = data_sent_server_list[5]["source"]
                source6 = data_sent_server_list[6]["source"]
                source7 = data_sent_server_list[7]["source"]
                source8 = data_sent_server_list[8]["source"]
                source9 = data_sent_server_list[9]["source"]
                
                data_sql = data_sent_server_list[0]["data_sql"]
                data_sql1 = data_sent_server_list[1]["data_sql"]
                data_sql2 = data_sent_server_list[2]["data_sql"]
                data_sql3 = data_sent_server_list[3]["data_sql"]
                data_sql4 = data_sent_server_list[4]["data_sql"]
                data_sql5 = data_sent_server_list[5]["data_sql"]
                data_sql6 = data_sent_server_list[6]["data_sql"]
                data_sql7 = data_sent_server_list[7]["data_sql"]
                data_sql8 = data_sent_server_list[8]["data_sql"]
                data_sql9 = data_sent_server_list[9]["data_sql"]
                
                if filename :
                    with open(source, 'r') as file:
                        file_content = file.read()
                        if len(file_content) > 0 and file_content == data_sql:
                            data_file = {'file_name': filename, 'file_content': file_content}
                        else :
                            upErr_Database(Time,Id_device)
                            by_pass = 1 
                if filename1 :
                    with open(source1, 'r') as file1:
                        file_content1 = file1.read()
                        if len(file_content1) > 0 and file_content1 == data_sql1:
                            data_file1 = {'file_name': filename1, 'file_content': file_content1}
                        else :
                            upErr_Database(Time1,Id_device1)
                            by_pass = 1 
                if filename2 :
                    with open(source2, 'r') as file2:
                        file_content2 = file2.read()
                        if len(file_content2) > 0 and file_content2 == data_sql2:
                            data_file2 = {'file_name': filename2, 'file_content': file_content2}
                        else :
                            upErr_Database(Time2,Id_device2)
                            by_pass = 1  
                if filename3 :
                    with open(source3, 'r') as file3:
                        file_content3 = file3.read()
                        if len(file_content3) > 0 and file_content3 == data_sql3:
                            data_file3 = {'file_name': filename3, 'file_content': file_content3}
                        else :
                            upErr_Database(Time3,Id_device3)
                            by_pass = 1 
                if filename4 :
                    with open(source4, 'r') as file4:
                        file_content4 = file4.read()
                        if len(file_content4) > 0 and file_content4 == data_sql4:
                            data_file4 = {'file_name': filename4, 'file_content': file_content4}
                        else :
                            upErr_Database(Time4,Id_device4)
                            by_pass = 1 
                if filename5 :
                    with open(source5, 'r') as file5:
                        file_content5 = file5.read()
                        if len(file_content5) > 0 and file_content5 == data_sql5:
                            data_file5 = {'file_name': filename5, 'file_content': file_content5}
                        else :
                            upErr_Database(Time5,Id_device5)
                            by_pass = 1 
                if filename6 :
                    with open(source6, 'r') as file6:
                        file_content6 = file6.read()
                        if len(file_content6) > 0 and file_content6 == data_sql6:
                            data_file6 = {'file_name': filename6, 'file_content': file_content6}
                        else :
                            upErr_Database(Time6,Id_device6)
                            by_pass = 1 
                if filename7 :
                    with open(source7, 'r') as file7:
                        file_content7 = file7.read()
                        if len(file_content7) > 0 and file_content7 == data_sql7:
                            data_file7 = {'file_name': filename7, 'file_content': file_content7}
                        else :
                            upErr_Database(Time7,Id_device7)
                            by_pass = 1 
                if filename8 :
                    with open(source8, 'r') as file8:
                        file_content8 = file8.read()
                        if len(file_content8) > 0 and file_content8 == data_sql8:
                            data_file8 = {'file_name': filename8, 'file_content': file_content8}
                        else :
                            upErr_Database(Time8,Id_device8)
                            by_pass = 1 
                if filename9 :
                    with open(source9, 'r') as file9:
                        file_content9 = file9.read()
                        if len(file_content9) > 0 and file_content9 == data_sql9:
                            data_file9 = {'file_name': filename9, 'file_content': file_content9}
                        else :
                            upErr_Database(Time9,Id_device9)
                            by_pass = 1 
                            
                if data_file and data_file1 and data_file2 and data_file3 and data_file4 and data_file5 and data_file6 and data_file7 and data_file8 and data_file9: 
                    json_data = {
                            "id": data_sent_server_list[0]["id"],
                            "id_device": data_sent_server_list[0]["id_device"],
                            "modbusdevice": data_sent_server_list[0]["modbusdevice"],
                            "data": data_sent_server_list[0]["data"],
                            "data_file" :data_file ,
                            
                            "id1": data_sent_server_list[1]["id"],
                            "id_device1": data_sent_server_list[1]["id_device"],
                            "modbusdevice1": data_sent_server_list[1]["modbusdevice"],
                            "data1": data_sent_server_list[1]["data"],
                            "data_file1" :data_file1 ,
                            
                            "id2": data_sent_server_list[2]["id"],
                            "id_device2": data_sent_server_list[2]["id_device"],
                            "modbusdevice2": data_sent_server_list[2]["modbusdevice"],
                            "data2": data_sent_server_list[2]["data"],
                            "data_file2" :data_file2 ,
                            
                            "id3": data_sent_server_list[3]["id"],
                            "id_device3": data_sent_server_list[3]["id_device"],
                            "modbusdevice3": data_sent_server_list[3]["modbusdevice"],
                            "data3": data_sent_server_list[3]["data"],
                            "data_file3" :data_file3 ,
                            
                            "id4": data_sent_server_list[4]["id"],
                            "id_device4": data_sent_server_list[4]["id_device"],
                            "modbusdevice4": data_sent_server_list[4]["modbusdevice"],
                            "data4": data_sent_server_list[4]["data"],
                            "data_file4" :data_file ,
                            
                            "id5": data_sent_server_list[5]["id"],
                            "id_device5": data_sent_server_list[5]["id_device"],
                            "modbusdevice5": data_sent_server_list[5]["modbusdevice"],
                            "data5": data_sent_server_list[5]["data"],
                            "data_file5" :data_file5 ,
                            
                            "id6": data_sent_server_list[6]["id"],
                            "id_device6": data_sent_server_list[6]["id_device"],
                            "modbusdevice6": data_sent_server_list[6]["modbusdevice"],
                            "data6": data_sent_server_list[6]["data"],
                            "data_file6" :data_file6,
                            
                            "id7": data_sent_server_list[7]["id"],
                            "id_device7": data_sent_server_list[7]["id_device"],
                            "modbusdevice7": data_sent_server_list[7]["modbusdevice"],
                            "data7": data_sent_server_list[7]["data"],
                            "data_file7" :data_file7 ,
                            
                            "id8": data_sent_server_list[8]["id"],
                            "id_device8": data_sent_server_list[8]["id_device"],
                            "modbusdevice8": data_sent_server_list[8]["modbusdevice"],
                            "data8": data_sent_server_list[8]["data"],
                            "data_file8" :data_file8 ,
                            
                            "id9": data_sent_server_list[9]["id"],
                            "id_device9": data_sent_server_list[9]["id_device"],
                            "modbusdevice9": data_sent_server_list[9]["modbusdevice"],
                            "data9": data_sent_server_list[9]["data"],
                            "data_file9" :data_file9 
                            
                            }
                    
                    files = [('files', (filename, open(source, 'rb'), 'text/plain')),
                            ('files', (filename1, open(source1, 'rb'), 'text/plain')),
                            ('files', (filename2, open(source2, 'rb'), 'text/plain')),
                            ('files', (filename3, open(source3, 'rb'), 'text/plain')),
                            ('files', (filename4, open(source4, 'rb'), 'text/plain')),
                            ('files', (filename5, open(source5, 'rb'), 'text/plain')),
                            ('files', (filename6, open(source6, 'rb'), 'text/plain')),
                            ('files', (filename7, open(source7, 'rb'), 'text/plain')),
                            ('files', (filename8, open(source8, 'rb'), 'text/plain')),
                            ('files', (filename9, open(source9, 'rb'), 'text/plain'))
                            ]
                    
                try:
                    if len(data_sent_server_list)==10 and by_pass == 0 :
                        response = requests.post(URL_SERVER_SYNC_FILE, data = json_data , files = files)
                        if response.status_code == 200:
                            # Step 3 : update data sync in database
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time ,id_device_fr_sys , Id_device))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time1 ,id_device_fr_sys , Id_device1))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time2 ,id_device_fr_sys , Id_device2))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time3 ,id_device_fr_sys , Id_device3))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time4 ,id_device_fr_sys , Id_device4))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time5 ,id_device_fr_sys , Id_device5))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time6 ,id_device_fr_sys , Id_device6))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time7 ,id_device_fr_sys , Id_device7))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time8 ,id_device_fr_sys , Id_device8))
                            MySQL_Update_V1(QUERY_UPDATE_DATABASE,(current_time,Time9 ,id_device_fr_sys , Id_device9))
                            print(response.json())
                            status_sync = 1
                            count = 0 
                        else:
                            print(response.json())
                            status_sync = 0
                            Executeup_Multi_NumberRetry_Database(time_retry, Time, Id_device,Time1, Id_device1,Time2, 
                                                                Id_device2,Time3, Id_device3,Time4, Id_device4,Time5, 
                                                                Id_device5,Time6, Id_device6,Time7, Id_device7,Time8, 
                                                                Id_device8,Time9, Id_device9)
                except Exception as e:
                    status_sync = 0 
                    Executeup_Multi_NumberRetry_Database(time_retry, Time, Id_device,Time1, Id_device1,Time2, 
                                                                Id_device2,Time3, Id_device3,Time4, Id_device4,Time5, 
                                                                Id_device5,Time6, Id_device6,Time7, Id_device7,Time8, 
                                                                Id_device8,Time9, Id_device9)
                    print('An exception occurred',e)
            else : 
                if len(Time)> 0 and len(str(Id_device))> 0 :
                    upErr_Database(Time,Id_device)
                if len(Time1)> 0 and len(str(Id_device1))> 0 :
                    upErr_Database(Time1,Id_device1)
                if len(Time2)> 0 and len(str(Id_device2))> 0 :
                    upErr_Database(Time2,Id_device2)
                if len(Time3)> 0 and len(str(Id_device3))> 0 :
                    upErr_Database(Time3,Id_device3)
                if len(Time4)> 0 and len(str(Id_device4))> 0 :
                    upErr_Database(Time4,Id_device4)
                if len(Time5)> 0 and len(str(Id_device5))> 0 :
                    upErr_Database(Time5,Id_device5)
                if len(Time6)> 0 and len(str(Id_device6))> 0 :
                    upErr_Database(Time6,Id_device6)
                if len(Time7)> 0 and len(str(Id_device7))> 0 :
                    upErr_Database(Time7,Id_device7)
                if len(Time8)> 0 and len(str(Id_device8))> 0 :
                    upErr_Database(Time8,Id_device8)
                if len(Time9)> 0 and len(str(Id_device9))> 0 :
                    upErr_Database(Time9,Id_device9)

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
    if len(Time) and len(str(id_device)) and flag_end_update == False:
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
# Describe Executeup_Multi_NumberRetry_Database
# /**
# 	 * @description execute when systemp is fault 
# 	 * @author bnguyen
# 	 * @since 17-1-2023
# 	 * @param {}
# 	 * @return 
# 	 */
def Executeup_Multi_NumberRetry_Database(time_retry, Time, id_device,Time1, id_device1,Time2, id_device2,Time3, id_device3,Time4, id_device4,Time5, id_device5,Time6, id_device6,Time7, id_device7,Time8, id_device8,Time9, id_device9):
    global count
    global status_sync
    global flag_end_update
    
    if count <= 4:
        count += 1
    if status_sync == 1:
        count = 0
        flag_end_update = False
        pass
    if len(Time) and len(str(id_device)) and flag_end_update == False:
        if count != 0 and status_sync == 0:
            if 1 <= time_retry <= 15 and status_sync == 0:
                scheduler = AsyncIOScheduler()
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time, id_device])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time1, id_device1])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time2, id_device2])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time3, id_device3])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time4, id_device4])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time5, id_device5])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time6, id_device6])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time7, id_device7])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time8, id_device8])
                scheduler.add_job(upNumberRetry_Database, 'cron', minute=time_retry, args=[Time9, id_device9])
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
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time1, id_device1])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time2, id_device2])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time3, id_device3])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time4, id_device4])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time5, id_device5])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time6, id_device6])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time7, id_device7])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time8, id_device8])
                scheduler.add_job(upNumberRetry_Database, 'cron', second="*/10", args=[Time9, id_device9])
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
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
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
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_GETDATA_SERVER or not QUERY_ALL_DEVICES or not QUERY_SYNC_SERVER or not QUERY_UPDATE_DATABASE or not QUERY_TIME_SYNC_DATA or not QUERY_UPDATE_ERR_DATABASE or not QUERY_TIME_RETRY or not QUERY_UPDATE_NUMBERRETRY or not QUERY_NUMER_FILE or not QUERY_SYNC_MULTIFILE_SERVER or not QUERY_SYNC_ERROR_MQTT:
        print("Error not found data in file mybatis")
        return -1
    try: 
        result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
        time_data_server = await MySQL_Select_v1(QUERY_GETDATA_SERVER)
    except Exception as e:
            print('An exception occurred',e)
    if not result_all or not time_data_server :
        print("Error not found data in Database")
        return -1
    if result_all and time_data_server :
        time_sentdata = time_data_server[0]["time_log_data_server"]
        time_sentdata = 100 # test 
        if time_sentdata and count <= 1 :
                if 0 <= time_sentdata <= 24:
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'cron', hour = time_sentdata,  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 95 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'interval', hours = "12",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 96 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'interval', hours = "8",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 97 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'interval', minutes = f"{time_sentdata}",  args=[URL_SERVER_SYNC])
                    scheduler.start()
                elif time_sentdata == 98 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'interval', minutes = "15",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 99 :
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'interval', hours = "1",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                elif time_sentdata == 100 : # test cron 
                    scheduler = AsyncIOScheduler()
                    scheduler.add_job(sync_Server_Database, 'cron', second = "*/10",  args=[URL_SERVER_SYNC,URL_SERVER_SYNC_FILE])
                    scheduler.start()
                
    scheduler = AsyncIOScheduler()
    scheduler.add_job(colectDatatoPushMQTT, 'interval', seconds = 5 , args=[MQTT_BROKER,
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
    



