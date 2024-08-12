# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import asyncio
import base64
import datetime
import gzip
import json
import os
import sys
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
from utils.libTime import *
from utils.mqttManager import (gzip_decompress, mqtt_public_common,
                               mqtt_public_paho, mqtt_public_paho_zip,
                               mqttService)

# Use passing parameters to file
# arr = sys.argv
# print(f'arr: {arr}')
# ------------------------------------

# Declare Variable 
gArrayListDeviceLogDBFromMQTT = []
gArrayListDeviceLogDBFromTableDeviceList = []
gArrayListDeviceMPPTFromMQTT = []
gStrStatusEachOfDevice = ""   
gIntErrorCodeOfDevice = 0
gStrMessageOfDevice = ""
gStrStatusOfDevice = ""
gStrStatusLogEachDevice = "Waiting for the record to finish"
gStrTimeIntervalLogDeviceInDB = ""
gArrayResultSerialNumberInDB = []
# Information Query
QUERY_TIME_CREATE_FILE = ""
QUERY_ALL_DEVICES = ""
QUERY_TIME_SYNC_DATA = ""
QUERY_SELECT_TOPIC = ""
# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
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
# ----- MQTT -----
# /**
# Describe process_message_result_list 
# 	 * @description process_message_result_list
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param { message}
# 	 * @return result_list
# 	 */ 
async def processGetMessageAllDeviceCreateListDeviceLogDeviceInDB(message):
    global gStrStatusEachOfDevice    
    global gStrMessageOfDevice 
    global gStrStatusOfDevice
    global gArrayListDeviceLogDBFromMQTT
    strNameOfDevice = ""
    arrayListDeviceLogDevice = {}
    
    try:
        current_time = get_utc()
        # create list data device from topic ALL devices 
        for items in message:
            deviceId = items["id_device"]
            gStrStatusEachOfDevice = items["status_device"]
            message = items["message"]
            gStrStatusOfDevice = items["status_register"]
            fields = items["fields"]
            strTpyeOfDevice = items["type_device_type"]
            strNameOfDevice = items["device_name"]
            if deviceId not in arrayListDeviceLogDevice:
                arrayListDeviceLogDevice[deviceId] = {
                    "id": int(deviceId),
                    "device_name":strNameOfDevice,
                    "point_id": [],
                    "data": [],
                    "namekey":[],
                    "time": current_time,
                    "status_device": gStrStatusEachOfDevice,
                    "gStrMessageOfDevice": gStrMessageOfDevice,
                    "status_register": gStrStatusOfDevice
                }
            
            # Condition log device 
            if strTpyeOfDevice != 1:      
                for field in fields:
                    if field['config'] != 'MPPT':
                        arrayListDeviceLogDevice[deviceId]["point_id"].append(str(field["id"]))
                        dataCorrespondingfield = str(field["value"]) if field["value"] is not None else 0.0
                        arrayListDeviceLogDevice[deviceId]["data"].append(dataCorrespondingfield)
                        arrayListDeviceLogDevice[deviceId]["namekey"].append(field["point_key"])
        # Convert dictionary to list
        gArrayListDeviceLogDBFromMQTT = list(arrayListDeviceLogDevice.values())
    except Exception as err:
        print(f"process_message_result_list : '{err}'")
# Describe processGetMessageAllDeviceCreateListDeviceMPTT 
# 	 * @description processGetMessageAllDeviceCreateListDeviceMPTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param { message}
# 	 * @return result_list_MPPT
# 	 */ 
async def processGetMessageAllDeviceCreateListDeviceMPTT(message):
    global gStrStatusEachOfDevice    
    global gStrMessageOfDevice 
    global gStrStatusOfDevice
    global gArrayListDeviceMPPTFromMQTT 

    deviceId = 0 
    strTpyeOfDevice = 0
    strNameDeviceType = ""
    dictionaryInforEachOfDevice = {}

    try:
        # create list data device from topic ALL devices 
        for items in message:
            deviceId = items["id_device"]
            fields = items["fields"]
            strNameDeviceType = items["name_device_type"]
            strTpyeOfDevice = items["type_device_type"]
            # Condition log device 
            if strTpyeOfDevice != 1 and strNameDeviceType == "PV System Inverter":      
                for field in fields:
                    if field['config'] == 'MPPT':
                        # Get data for table mppt 
                        MPPTVolt = field['value']['mppt_volt']
                        MPPTAmps = field['value']["mppt_amps"]
                        MPPTpoint_key_strings = field['value']["mppt_string"]
                        MPPTpoint_key = field['point_key']
                        for item_string in MPPTpoint_key_strings:
                            MPPTpoint_key_string = item_string['point_key']
                        
                        key_mppt = (int(deviceId), MPPTpoint_key, MPPTpoint_key_string)
                        if key_mppt in dictionaryInforEachOfDevice:
                            # If the object already exists, update the values
                            dictionaryInforEachOfDevice[key_mppt]['MPPTVolt'] = MPPTVolt
                            dictionaryInforEachOfDevice[key_mppt]['MPPTAmps'] = MPPTAmps
                        else:
                            # If it does not exist, add a new object to the dictionary
                            dictionaryInforEachOfDevice[key_mppt] = {
                                "id": int(deviceId),
                                "point_key": MPPTpoint_key,
                                "point_key_string": MPPTpoint_key_string,
                                "MPPTVolt": MPPTVolt,
                                "MPPTAmps": MPPTAmps
                            }
                        # Pass the values ​​from the dictionary into result_list_MPPT
                        gArrayListDeviceMPPTFromMQTT = list(dictionaryInforEachOfDevice.values())
    except Exception as err:
        print(f"processGetMessageAllDeviceCreateListDeviceMPTT_list: '{err}'")
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
            # payload = json.loads(message.message.decode())
            payload = gzip_decompress(message.message)
            await processGetMessageAllDeviceCreateListDeviceLogDeviceInDB(payload)
            await processGetMessageAllDeviceCreateListDeviceMPTT(payload)
        except Exception as err:
            print(f"Error handle_messages_driver: '{err}'")
# Describe processSudAllMessageFromMQTT 
# 	 * @description processSudAllMessageFromMQTT
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def processSudAllMessageFromMQTT(host, port, username, password, serial_number_project):
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
        print(f"Error MQTT processSudAllMessageFromMQTT: '{err}'")
# Describe processInsertListDeviceFromMQTT
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
# async def processInsertListDeviceFromMQTT():
#     global result_list
#     manysql_queries = {}
#     for item in result_list:
#         sql_id = item["id"]
#         result_sql_queries = await processInsertEachDeviceFromListMQTT(sql_id)
#         if result_sql_queries:
#             manysql_queries[sql_id] = result_sql_queries
#     MySQL_Insert_v3(manysql_queries)
async def processInsertListDeviceFromMQTT():
    global gArrayListDeviceLogDBFromMQTT
    tasks = []
    for item in gArrayListDeviceLogDBFromMQTT:
        deviceId = item["id"]
        task = processInsertEachDeviceFromListMQTT(deviceId)
        tasks.append(task)
    await asyncio.gather(*tasks)
# Describe processInsertEachDeviceFromListMQTT
# /**
# 	 * @description create query from result_list
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {sql_id, gArrayListDeviceLogDBFromTableDeviceList}
# 	 * @return queries 
# 	 */
async def processInsertEachDeviceFromListMQTT(IdDeviceFromListMQTTAll):
    global gArrayListDeviceLogDBFromMQTT
    global gStrStatusLogEachDevice
    global gStrStatusEachOfDevice 
    global gStrStatusOfDevice
    global gIntErrorCodeOfDevice
    dictionaryQueriesEachOfDevice = {}
    arrayDataUsingLogDB = []
    arrayFieldOfDevice = []
    # Filter Information Device From List All = IdDeviceFromListMQTTAll
    DictID = [item for item in gArrayListDeviceLogDBFromMQTT if item["id"] == IdDeviceFromListMQTTAll]

    if DictID:
        arrayDataUsingLogDB = DictID[0]["data"]
        gStrStatusEachOfDevice = DictID[0]["status_device"]
        gStrStatusOfDevice = DictID[0]["status_register"]
        arrayFieldOfDevice = DictID[0]["namekey"]
    # Check data if data empty
    if not arrayDataUsingLogDB: 
        arrayDataUsingLogDB = [None] * len(arrayFieldOfDevice)
    # Check status register device
    if gStrStatusEachOfDevice == "offline" :
        gIntErrorCodeOfDevice = 139
    elif gStrStatusEachOfDevice == "online" :
        if len(gStrStatusOfDevice) > 0 :
            gIntErrorCodeOfDevice = gStrStatusOfDevice[0]["ERROR_CODE"]
        else :
            gIntErrorCodeOfDevice = 0

    try:
        # Write data to corresponding devices in the database
        timeCurrent = get_utc()
        ValueInsertInDB = (timeCurrent, IdDeviceFromListMQTTAll , gIntErrorCodeOfDevice) + tuple(arrayDataUsingLogDB)
        # Replace '0.0' with '' in the data tuple
        ValueInsertInDB = tuple("0.0" if x == "" else x for x in ValueInsertInDB)
        # Create Query
        columns = ["time", "id_device", "error"]
        for itemp in arrayFieldOfDevice:
            columns.append(itemp)
        tableNameDeviceInDB = f"dev_{IdDeviceFromListMQTTAll}"
        # Create a query with REPLACE INTO syntax
        queryInsertDataDeviceInDB = f"INSERT INTO {tableNameDeviceInDB} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        dictionaryQueriesEachOfDevice[IdDeviceFromListMQTTAll] = [queryInsertDataDeviceInDB, ValueInsertInDB]
        # Execute the query
        MySQL_Insert_v3(dictionaryQueriesEachOfDevice)
    except Exception as e:
        print(f"Error during file creation is : {e}")
    return dictionaryQueriesEachOfDevice
# /**
# 	 * @description 
#       - create and write data in file  
#       - sync data file with database 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port, topic, username, password}
# 	 * @return result_list 
# 	 */ 
async def processInsertDeviceMPTTFromListMQTT():
    global gArrayListDeviceMPPTFromMQTT
    arrayValueListDeviceMPTTFromMQTT = []
    arrayValueListDeviceMPTTSttingFromMQTT = []
    deviceId = ""
    MPPTKey = ""
    MPPTKey_string = ""
    voltageDeviceMPTT = ""
    currentDeviceMPTT = ""
    queryUpdateDeviceMPPT = ""
    queryUpdateDeviceMPPTString = ""
    try:
        if gArrayListDeviceMPPTFromMQTT :
            for item in gArrayListDeviceMPPTFromMQTT:
                if 'id' in item and 'point_key' in item and 'point_key_string' in item and 'MPPTVolt' in item and 'MPPTAmps' in item:
                    deviceId = item['id']
                    MPPTKey = item['point_key']
                    MPPTKey_string = item['point_key_string']
                    voltageDeviceMPTT = item['MPPTVolt']
                    currentDeviceMPTT = item['MPPTAmps']
                    # get Information about Device From MQTT
                    arrayValueListDeviceMPTTFromMQTT.append((voltageDeviceMPTT, currentDeviceMPTT, deviceId, MPPTKey))
                    arrayValueListDeviceMPTTSttingFromMQTT.append((currentDeviceMPTT, deviceId, MPPTKey_string))
            # Execute query 
            queryUpdateDeviceMPPT = "UPDATE device_mppt SET voltage = %s, current = %s WHERE id_device_list = %s AND namekey = %s;"
            MySQL_Insert_v4(queryUpdateDeviceMPPT, arrayValueListDeviceMPTTFromMQTT)
            queryUpdateDeviceMPPTString = "UPDATE device_mppt_string SET current = %s WHERE id_device_mppt = %s AND namekey = %s;"
            MySQL_Insert_v4(queryUpdateDeviceMPPTString, arrayValueListDeviceMPTTSttingFromMQTT)
            # Reset List Device MQTT 
            gArrayListDeviceMPPTFromMQTT = []
    except Exception as e:
        print(f"Error during data insertion: {e}")
# Describe processFeedbackStatusLogDeviceSentMqttAllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def processFeedbackStatusLogDeviceSentMqttAllDevice(host, port,serialNumber, username, password):
    global QUERY_SELECT_TOPIC 
    global gArrayListDeviceLogDBFromMQTT
    global gArrayResultSerialNumberInDB
    
    topic = serialNumber + "/LogDevice"  
    tasks = []
    for item in gArrayListDeviceLogDBFromMQTT:
        sql_id = item["id"]
        task = processFeedbackStatusLogDeviceSentMqttEachDevice(sql_id,host, port,topic, username, password)
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
async def processFeedbackStatusLogDeviceSentMqttEachDevice(IdDeviceGetListMQTT,host, port,topic, username, password):
    
    global gStrStatusEachOfDevice 
    global gArrayListDeviceLogDBFromMQTT
    global gStrStatusLogEachDevice 
    global gStrTimeIntervalLogDeviceInDB
    global gArrayListDeviceLogDBFromMQTT
    
    timeCurrent = get_utc()
    arrayDataOfDevice = []
    strSqlID = ""
    gStrNameOfDevice = ""
    
    DictID = [item for item in gArrayListDeviceLogDBFromMQTT if item["id"] == IdDeviceGetListMQTT]
    if DictID:
        arrayDataOfDevice = DictID[0]["data"]
    try:
        gJsonFeedbackStatusLogFileSentMqtt={
            "id_device":IdDeviceGetListMQTT,
            "status_chanel":gStrStatusLogEachDevice,
            "time_stamp" :timeCurrent,
            "time_log": gStrTimeIntervalLogDeviceInDB ,
            "data_log":arrayDataOfDevice,
            }
        
        # File creation time 
        strSqlID = str(IdDeviceGetListMQTT)
        gStrNameOfDevice = [item['device_name'] for item in gArrayListDeviceLogDBFromMQTT if item['id'] == IdDeviceGetListMQTT][0] 
        
        mqtt_public_paho_zip(host,
                port,
                topic + f"/"+strSqlID+"|"+gStrNameOfDevice,
                username,
                password,
                gJsonFeedbackStatusLogFileSentMqtt)
    except Exception as err:
        print('Error processFeedbackStatusLogDeviceSentMqttEachDevice : ',err)

async def main():
    
    global QUERY_TIME_CREATE_FILE
    global QUERY_TIME_SYNC_DATA
    global QUERY_SELECT_TOPIC
    global MQTT_BROKER
    global MQTT_PORT
    global MQTT_TOPIC_SUB
    global MQTT_USERNAME
    global MQTT_PASSWORD
    
    global gStrTimeIntervalLogDeviceInDB
    global gArrayResultSerialNumberInDB
    gArrayListDeviceLogDBFromTableDeviceList = []
    
    result_mybatis = get_mybatis('/mybatis/logfile.xml')
    try:
        QUERY_TIME_CREATE_FILE = result_mybatis["QUERY_TIME_CREATE_FILE"]
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TIME_SYNC_DATA = result_mybatis["QUERY_TIME_SYNC_DATA"]
        QUERY_SELECT_TOPIC = result_mybatis["QUERY_SELECT_TOPIC"]
    except Exception as e:
            print('An exception occurred',e)
    if not QUERY_TIME_CREATE_FILE or not QUERY_ALL_DEVICES  or not QUERY_TIME_SYNC_DATA or not QUERY_SELECT_TOPIC:
        print("Error not found data in file mybatis") 
        return -1
    #------------------------------------------------------------------------
    timeCycleSaveDataInTableDevice = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    gArrayListDeviceLogDBFromTableDeviceList = await MySQL_Select_v1(QUERY_ALL_DEVICES)
    gArrayResultSerialNumberInDB = await MySQL_Select_v1(QUERY_SELECT_TOPIC)
    # Get Serial Number
    if gArrayResultSerialNumberInDB != None :
        serialNumber = gArrayResultSerialNumberInDB[0]["serial_number"]
        MQTT_TOPIC_SUB = str(serialNumber) + "/Devices/#"
        # Get Time Log data in table 
        item = timeCycleSaveDataInTableDevice[0]
        gStrTimeIntervalLogDeviceInDB = item["time_log_interval"]
        position = gStrTimeIntervalLogDeviceInDB.rfind("minute")
        number = gStrTimeIntervalLogDeviceInDB[:position]
        int_number = int(number)
        if not gArrayListDeviceLogDBFromTableDeviceList :
            print("None of the devices have been selected in the database")
            return -1
        if not timeCycleSaveDataInTableDevice :
            print("Unable to select synchronization time for data in the database.")
            return -1
        # Task execute
        scheduler = AsyncIOScheduler()
        scheduler.add_job(processInsertListDeviceFromMQTT, 'cron', minute = f'*/{int_number}')
        scheduler.add_job(processInsertDeviceMPTTFromListMQTT, 'cron', minute = f'*/{int_number}')
        scheduler.add_job(processFeedbackStatusLogDeviceSentMqttAllDevice, 'cron',  second = f'*/10' , args=[MQTT_BROKER,
                                                                                MQTT_PORT,
                                                                                serialNumber,
                                                                                MQTT_USERNAME,
                                                                                MQTT_PASSWORD])
        scheduler.start()
        tasks = []
        tasks.append(processSudAllMessageFromMQTT(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            serialNumber,
                            ))
        await asyncio.gather(*tasks, return_exceptions=False)
    #-------------------------------------
    await asyncio.sleep(0.05)
if __name__ == "__main__":
    asyncio.run(main())


