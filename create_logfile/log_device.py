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
async def update_data_for_device_in_database():
    
    result_mybatis=get_mybatis('/mybatis/logfile.xml')
    QUERY_ALL_DEVICES=result_mybatis["QUERY_ALL_DEVICES"]
    QUERY_TIME_CREATE_FILE=result_mybatis["QUERY_TIME_CREATE_FILE"]
    
    if  QUERY_ALL_DEVICES  != -1 and QUERY_TIME_CREATE_FILE  != -1 :
        pass
    else:           
        print("Error not found data in file mybatis")
        return -1
    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    time_create_file_insert_data_table_dev = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    #---------------------------------------------------------------------------------------------------------------
    while True:
        current_time = get_utc()
        current_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        year,month, day, hour, minute, second = current_datetime.year , current_datetime.month,current_datetime.day,current_datetime.hour, current_datetime.minute, current_datetime.second  
        global result_list
        data_to_write =""
        point_id = ""
        
        #-----------------------------------------------------
        for item in time_create_file_insert_data_table_dev:
            time = item["time_log_interval"]
            position = time.rfind("minute")
            number = time[:position]
            int_number = int(number)
        
        # File creation time 
            if minute % int_number == 0 and second % 10 == 0:
                for item in result_all:
                    sql_id = item["id"]
                    
                    DictID = [item for item in result_list if item["id"] == sql_id]
                    
                    for item in DictID:
                        data = item["data"]
                        data_to_write = data
                        
                    for item in DictID:
                        point_id = item["point_id"]
                    try:
                            # Write data to corresponding devices in the database-------------
                            if data_to_write :
                                time_insert_dev = get_utc()
                                value_insert = (time_insert_dev, sql_id ) + tuple(data_to_write) 
                                MySQL_Insert_v2(f'dev_{sql_id:05d}', point_id ,value_insert)       
                                
                                print(f"ghi data vào database dev0000 thành công theo chu kì {int_number} phút 10s ")
                            else :
                                print(f"ghi data vào thành công theo chu kì {int_number} phút 10s và danh sách ghi vào rỗng ")
                            # ----------------------------------------------------------------
                    except Exception as e:
                        print(f"Error during file creation is : {e}")
            await asyncio.sleep(1)
    
async def main():
    tasks = []
    tasks.append(asyncio.create_task(update_data_for_device_in_database ()))
                                                    
    tasks.append(asyncio.create_task(get_data_from_MQTT(MQTT_BROKER,
                                                            MQTT_PORT,
                                                            MQTT_TOPIC_SUB,
                                                            MQTT_USERNAME,
                                                            MQTT_PASSWORD
                                                            )))
    await asyncio.gather(*tasks, return_exceptions=False)
    #-------------------------------------
    
if __name__ == "__main__":
    asyncio.run(main())