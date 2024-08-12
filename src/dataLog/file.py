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

# from config import *
# from test.libMySQL import *

# Use passing parameters to file
arr = sys.argv
# print(f'arr: {arr}')
# ------------------------------------
gArrayListDeviceLogFile =[]
gArrayListValueInsertDataInTableSync = []
gArrayListDeviceNeedLogFile = []
countMonitor = 0

# Declare Variable 
gStrStatusEachOfDevice = ""     
gStrStatusOfRegister = ""
gStrStatusOfFile = "Success"
gJsonFeedbackStatusLogFileSentMqtt = ""
gStrNameOfFile = ""
strDataUsingLogFile = ""
gStrTimeCreateNameFile = ""
gStrCycleTimeLogFile = ""
gArrayResultCycleTimeLogFileInDB = ""

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
MQTT_TOPIC_SUB_MESSAGE_ALL_DEVICE = ""
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
#--------------------------------------------------------------------
# /**
# Describe processGetMessageAllDeviceCreateListDeviceLogFile 
# 	 * @description processGetMessageAllDeviceCreateListDeviceLogFile
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param { message}
# 	 * @return result_list
# 	 */ 
async def processGetMessageAllDeviceCreateListDeviceLogFile(messageAllDevice):
    global gStrStatusEachOfDevice    
    global gStrStatusOfRegister
    global gArrayListDeviceLogFile
    global gStrStatusOfFile
    dictionaryInforEachOfDevice = {}
    try:
        currentTime = get_utc()
        # create list data device from topic ALL devices 
        for items in messageAllDevice:
            deviceId = items["id_device"]
            gStrStatusEachOfDevice = items["status_device"]
            gStrStatusOfRegister = items["status_register"]
            listFieldsOfDevice = items["fields"]
            typeOfDevice = items["type_device_type"]
            if deviceId not in dictionaryInforEachOfDevice:
                dictionaryInforEachOfDevice[deviceId] = {
                    "id": int(deviceId),
                    "point_id": [],
                    "data": [],
                    "time": currentTime,
                    "status_device": gStrStatusEachOfDevice,
                    "status_register": gStrStatusOfRegister
                }
            # Condition log device 
            if typeOfDevice != 1:      
                for field in listFieldsOfDevice:
                    if field['config'] != 'MPPT':
                        dictionaryInforEachOfDevice[deviceId]["point_id"].append(str(field["id"]))
                        dataCorrespondingfield = str(field["value"]) if field["value"] is not None else ""
                        dictionaryInforEachOfDevice[deviceId]["data"].append(dataCorrespondingfield)
        # Convert dictionary to list
        gArrayListDeviceLogFile = list(dictionaryInforEachOfDevice.values())
    except Exception as err:
        print(f"processGetMessageAllDeviceCreateListDeviceLogFile : '{err}'")
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
# 	 * @description handleMessageDriver
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {client}
# 	 * @return all topic , all message
# 	 */ 
async def handleMessageDriver(client):
    while True:
        try:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            # payload = json.loads(message.message.decode())
            payload = gzip_decompress(message.message)
            await processGetMessageAllDeviceCreateListDeviceLogFile(payload)
        except Exception as err:
            print(f"Error handleMessageDriver: '{err}'")
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
            await handleMessageDriver(client)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT processSudAllMessageFromMQTT: '{err}'")
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
async def processCreateFileCycle(base_path,arrayIdChanel,head_file):
    # Query Global
    global QUERY_TIME_SYNC_DATA
    global QUERY_SELECT_COUNT_POINT_LIST
    global QUERY_INSERT_SYNC_DATA
    
    # Variable Global
    global gStrStatusEachOfDevice    
    global gStrStatusOfRegister
    global gArrayListDeviceLogFile
    global gStrStatusOfFile
    global gArrayListValueInsertDataInTableSync
    global strDataUsingLogFile
    global gStrNameOfFile
    global gStrTimeCreateNameFile
    global countMonitor 
    
    # Get information from SQL
    intIdChanel = arrayIdChanel[1]
    gArrayListDeviceNeedLogFile = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(intIdChanel,))
    
    # Take time to create file 
    informationTableUploadChannel = MySQL_Select(QUERY_TIME_SYNC_DATA,(intIdChanel,))
    currentTime = get_utc()
    currentDateTime = datetime.datetime.strptime(currentTime, "%Y-%m-%d %H:%M:%S")
    year,month, day = currentDateTime.year , currentDateTime.month,currentDateTime.day
    
    # Declare Variable
    timeMessageAll = currentTime
    valueInsertTable =""
    dataOfDevice =""
    typeOfFile = ""
    #----------------------------------------------------------------------------
        
    for item in informationTableUploadChannel:
        typeOfFile = item["type_protocol"]
        
    for item in gArrayListDeviceNeedLogFile:
        idDevice = item["id"]
        # Get information create file in DB 
        modbus_device = [item['rtu_bus_address'] for item in gArrayListDeviceNeedLogFile if item['id'] == idDevice][0]
        arrayNumberPointList = MySQL_Select(QUERY_SELECT_COUNT_POINT_LIST,(idDevice,))
        NumberPointList = arrayNumberPointList[0]['COUNT(*)']
        dictInformationFolowIDdevice = [item for item in gArrayListDeviceLogFile if item["id"] == idDevice]
        # get information about device folow id device
        if dictInformationFolowIDdevice:
            data = dictInformationFolowIDdevice[0]["data"]
            dataOfDevice = data
            timeMessageAll = dictInformationFolowIDdevice[0]["time"]
        # Create file create path
        fileCreationPath = os.path.join(base_path, f"{intIdChanel}\\{typeOfFile}\\{idDevice}\\{year}\\{month}\\{day}")
        try:
            #Create file path 
            os.makedirs(fileCreationPath, exist_ok=True)
            time_file = get_utc()
            time_file_datetime = datetime.datetime.strptime(currentTime, "%Y-%m-%d %H:%M:%S")
            gStrTimeCreateNameFile = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
            gStrNameOfFile = f'{head_file}-{idDevice:03d}.{gStrTimeCreateNameFile}.log'
            file_path = os.path.join(fileCreationPath, gStrNameOfFile)
            source_file = fileCreationPath + "/" + gStrNameOfFile
            # Create data in file 
            if not dataOfDevice:
                strDataUsingLogFile = ["" for i in range(NumberPointList)]
            else:
                strDataUsingLogFile = [str(val) for val in dataOfDevice]
            # write data in file  
            with open(file_path, 'w') as file:
                formatted_time2 = "'" + time_file + "'"
                file.write(f'{formatted_time2},0,0,0,{",".join(strDataUsingLogFile)}')
                if countMonitor < 2 :
                    countMonitor += 1 
                # create data in DB ------------------------------------------------------------------
                realTime = get_utc()
                valueInsertTable = (realTime, idDevice, modbus_device, fileCreationPath, source_file, gStrNameOfFile, realTime,f'{formatted_time2},0,0,0,{",".join(strDataUsingLogFile)}', intIdChanel)
                for index, item in enumerate(gArrayListValueInsertDataInTableSync):
                    if item[1] == idDevice:
                        # Update the SQL query
                        gArrayListValueInsertDataInTableSync[index] = valueInsertTable
                        break
                else:
                    # Add a new entry to the list
                    gArrayListValueInsertDataInTableSync.append(valueInsertTable)
                # code pud data MQTT ----------------------------------------------------------------- 
                gStrStatusOfFile = "Success"
                currentTimeConvert = datetime.datetime.strptime(currentTime, "%Y-%m-%d %H:%M:%S").timestamp()
                timeMessageAllConvert = datetime.datetime.strptime(timeMessageAll, "%Y-%m-%d %H:%M:%S").timestamp()
                if currentTimeConvert - timeMessageAllConvert < 10 :
                    gStrStatusEachOfDevice ="NEW"
                else :
                    gStrStatusEachOfDevice ="OLD"
                #----------------------------------------------------------------- 
        except Exception as e:
            gStrStatusOfFile = "Fault"
            print(f"Error during file creation is : {e}")
# Describe processFeedbackStatusLogFileSentMqttAllDevice
# /**
# 	 * @description Multi-threaded running of devices in the database
# 	 * @author bnguyen
# 	 * @since 12/3/2024
# 	 * @param {}
# 	 * @return 
# 	 */
async def processFeedbackStatusLogFileSentMqttAllDevice(arrayIdChanel,serialNumber,head_file,host, port, username, password):
    global QUERY_ALL_DEVICES_SYNCDATA
    intIdChanel = arrayIdChanel[1]
    gArrayListDeviceNeedLogFile = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (intIdChanel,))
    topic = serialNumber + "/LogFile" 
    tasks = []
    for item in gArrayListDeviceNeedLogFile:
        sql_id = item["id"]
        task = processFeedbackStatusLogFileSentMqttEachDevice(sql_id,arrayIdChanel,head_file,host, port,topic, username, password)
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
async def processFeedbackStatusLogFileSentMqttEachDevice(IdDeviceGetListMQTT,arrayIdChanel,head_file,host, port,topic, username, password):
    global gJsonFeedbackStatusLogFileSentMqtt
    global gStrStatusEachOfDevice 
    global gStrStatusOfFile
    global strDataUsingLogFile
    global gStrNameOfFile
    global gArrayListDeviceLogFile
    global gStrTimeCreateNameFile
    global gStrCycleTimeLogFile
    global countMonitor
    
    strSqlID = ""
    strNameDevice = ""
    arrayDataOfDevice = []
    currentTime = get_utc()
    timeGetMessageAllDevice = get_utc()

    intIdChanel = arrayIdChanel[1]
    gArrayListDeviceNeedLogFile = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA, (intIdChanel,))
    informationTableUploadChannel = MySQL_Select(QUERY_TIME_SYNC_DATA,(intIdChanel,))
    
    for item in informationTableUploadChannel:
        typeOfFile = item["type_protocol"]
    
    if IdDeviceGetListMQTT :
        gStrNameOfFile = f'{head_file}-{IdDeviceGetListMQTT:03d}.{gStrTimeCreateNameFile}.txt'
        DictID = [item for item in gArrayListDeviceLogFile if item["id"] == IdDeviceGetListMQTT]
        if DictID:
            timeGetMessageAllDevice = DictID[0]["time"]
            arrayDataOfDevice = DictID[0]["data"]  
        try: 
            if gStrTimeCreateNameFile :
                gJsonFeedbackStatusLogFileSentMqtt={
                    "id_device":IdDeviceGetListMQTT,
                    "status_data":gStrStatusEachOfDevice,
                    "status_chanel":gStrStatusOfFile,
                    "file_name":gStrNameOfFile,
                    "time_stamp" :currentTime,
                    "time_online" :timeGetMessageAllDevice,
                    "time_log": gStrCycleTimeLogFile,
                    "data_log":arrayDataOfDevice,
                    }
            else :
                gStrStatusOfFile = "fault"
                gJsonFeedbackStatusLogFileSentMqtt={
                    "id_device":IdDeviceGetListMQTT,
                    "status_data":"old",
                    "status_chanel":"no_files_yet",
                    "file_name":"No files yet",
                    "time_stamp" :currentTime,
                    "time_online" :timeGetMessageAllDevice,
                    "time_log": gStrCycleTimeLogFile,
                    "data_log":"No files yet",
                    }

            # File creation time 
            strSqlID = str(IdDeviceGetListMQTT)
            strNameDevice = [item['name'] for item in gArrayListDeviceNeedLogFile if item['id'] == IdDeviceGetListMQTT][0] 
            mqtt_public_paho_zip(host,
                    port,
                    topic + f"/Channel{intIdChanel}|{typeOfFile}/"+strSqlID+"|"+strNameDevice,
                    username,
                    password,
                    gJsonFeedbackStatusLogFileSentMqtt)
        except Exception as err:
            print('Error processFeedbackStatusLogFileSentMqttEachDevice : ',err)
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
async def processInsertDataInTableSyncData(arrayIdChanel):
    # Variable Global
    global QUERY_INSERT_SYNC_DATA_EXECUTEMANY
    global gArrayListValueInsertDataInTableSync
    global gStrStatusOfFile 
    intIdChanel = arrayIdChanel[1]
    gArrayListDeviceNeedLogFile = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(intIdChanel,))
    # File creation time 
    
    if len(gArrayListDeviceNeedLogFile) == len(gArrayListValueInsertDataInTableSync):
        MySQL_Insert_v4(QUERY_INSERT_SYNC_DATA_EXECUTEMANY,gArrayListValueInsertDataInTableSync)
    else :
        pass
# /**
# 	 * @description Insert data to Database
# 	 * @author bnguyen
# 	 * @since 04-01-2024
# 	 * @param {}
# 	 * @return  
# 	 */ 
async def processDeleteDataInTableSyncDataFolowCycle():
    try:
        # Delete rows from project_setup table where synced = 1
        query = "DELETE FROM sync_data WHERE synced = 1;"
        resultDeleteData = MySQL_Delete(query)
        print(f"Deleted {resultDeleteData.rowcount} rows from sync_data table")
    except Exception as err:
        print(f"Error MQTT subscribe processDeleteDataInTableSyncDataFolowCycle: '{err}'")
        
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
    global MQTT_TOPIC_SUB_MESSAGE_ALL_DEVICE
    global MQTT_USERNAME
    global MQTT_PASSWORD

    # Variable global
    global gStrCycleTimeLogFile
    
    strSerialNumber = ""
    gArrayListDeviceNeedLogFile = []
    arrayResultSerialNumber = []
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
        gArrayListDeviceNeedLogFile = MySQL_Select(QUERY_ALL_DEVICES_SYNCDATA,(arr[1],))
        gArrayResultCycleTimeLogFileInDB = await MySQL_Select_v1(QUERY_TIME_CREATE_FILE)
    # Get serial number from DB
    arrayResultSerialNumber = await MySQL_Select_v1(QUERY_SELECT_TOPIC)
    if arrayResultSerialNumber != None :
        strSerialNumber = arrayResultSerialNumber[0]["serial_number"]
        MQTT_TOPIC_SUB_MESSAGE_ALL_DEVICE = str(strSerialNumber) + "/Devices/#"
        
        if not gArrayListDeviceNeedLogFile :
            print("None of the devices have been selected in the database (check table upload_channel_device_map , divice_list)")
            return -1
        if not gArrayResultCycleTimeLogFileInDB :
            print("Unable to select synchronization time for data in the database.")
            return -1
        #  Get time log file from DB
        item = gArrayResultCycleTimeLogFileInDB[0]
        gStrCycleTimeLogFile = item["time_log_interval"]
        position = gStrCycleTimeLogFile.rfind("minute")
        number = gStrCycleTimeLogFile[:position]
        int_number = int(number)
        #-------------------------------------------------------
        scheduler = AsyncIOScheduler()
        scheduler.add_job(processCreateFileCycle, 'cron',  minute = f'*/{int_number}', args=[FOLDER_PATH,
                                                                                    arr,
                                                                                    HEAD_FILE_LOG,
                                                                                    ])
        scheduler.add_job(processFeedbackStatusLogFileSentMqttAllDevice, 'cron',  second = f'*/13' , args=[arr,
                                                                                strSerialNumber,
                                                                                HEAD_FILE_LOG,
                                                                                MQTT_BROKER,
                                                                                MQTT_PORT,
                                                                                MQTT_USERNAME,
                                                                                MQTT_PASSWORD])
        scheduler.add_job(processInsertDataInTableSyncData, 'cron',  minute = f'*/{int_number}', second=1, args=[arr])
        scheduler.add_job(processDeleteDataInTableSyncDataFolowCycle, 'interval', hours=1, args=[])
        scheduler.start()
        #-------------------------------------------------------
        tasks = []
        tasks.append(asyncio.create_task(processSudAllMessageFromMQTT(MQTT_BROKER,
                                                MQTT_PORT,
                                                MQTT_USERNAME,
                                                MQTT_PASSWORD,
                                                strSerialNumber
                                                )))
        
        # Move the gather outside the loop to wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        pass
if __name__ == "__main__":
    asyncio.run(main())