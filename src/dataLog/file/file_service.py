# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import asyncio
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import DBSessionManager
from utils.MQTTService import *
from utils.libTime import *
from utils.libMySQL import *
from dbService.syncData import SyncDataService
from dbService.deviceList import deviceListService
from dbService.uploadChannel import UploadChannelService

class LogFile:
    def __init__(self):
        self.message_log_file = []  
        self.list_device_log_file = []  
        self.time_create_file = ""
        self.value_insert_db = []
        
    # MQTT
    async def handle_mqtt_message(self, mqtt_service, message, time_interval_log_device,IdChannel,Head_File_Log,typeOfFile):
        try:
            if message:
                await self.create_threading_push_status_log_device(mqtt_service, time_interval_log_device,IdChannel,Head_File_Log,typeOfFile)
                if self.list_device_log_file:
                    self.message_log_file = await self.create_message_log_file(message)
                
        except Exception as err:
            print(f"Error handling MQTT message: '{err}'")
            
    async def create_threading_push_status_log_device(self, mqtt_service, timeLog,IdChannel,Head_File_Log,typeOfFile):
        db_new = await DBSessionManager.get_db()
        tasks = []
        self.list_device_log_file = await deviceListService.selectDevicesByUploadChannelID(db_new,IdChannel)
        if self.list_device_log_file:
            for item in self.list_device_log_file:
                sql_id = item["id"]
                task = self.push_status_log_file(mqtt_service, timeLog, sql_id,IdChannel,Head_File_Log,typeOfFile)
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def push_status_log_file(self, mqtt_service, timeLog, IdDeviceGetListMQTT, IdChannel, Head_File_Log,typeOfFile):
        topic = ""
        message = ""
        try:
            topic = await self.create_topic(IdChannel, typeOfFile, IdDeviceGetListMQTT)
            message = await self.create_message(IdDeviceGetListMQTT,Head_File_Log,timeLog)
            if topic and message :
                MQTTService.push_data_zip(mqtt_service, topic, message)
                MQTTService.push_data(mqtt_service, topic + "Binh", message)
        except Exception as err:
            print('Error processFeedbackStatusLogDeviceSentMqttEachDevice: ', err)

    async def get_type_of_file(self, IdChannel):
        db_new = await DBSessionManager.get_db()
        typeOfFile = await UploadChannelService.select_type_log_file(db_new, IdChannel)
        return typeOfFile

    async def create_topic(self, IdChannel, typeOfFile, IdDeviceGetListMQTT):
        strSqlID = str(IdDeviceGetListMQTT)
        gStrNameOfDevice = [item['device_name'] for item in self.message_log_file if item['id'] == IdDeviceGetListMQTT][0]
        topic = f"/LogFile/Channel{IdChannel}|{typeOfFile}/{strSqlID}|{gStrNameOfDevice}"
        return topic
    
    async def create_message(self ,IdDevice, Head_File_Log, timeLog):
        DictID = [item for item in self.message_log_file if item["id"] == IdDevice]
        if DictID:
            data = DictID[0]["data"]
            status_device = DictID[0]["status_device"]
            message = {
                "time_stamp": get_utc(),
                "id_device": IdDevice,
                "name_file": f'{Head_File_Log}-{IdDevice:03d}.{self.time_create_file}.log',
                "status_device": status_device,
                "time_log": timeLog,
                "data_log": data,
            }
            return message
        return None
    # create message log file 
    async def create_message_log_file(self, messageAllDevice):
        dict_device = {}
        list_id_filter = {item["id"] for item in self.list_device_log_file}
        try:
            currentTime = get_utc()
            for items in messageAllDevice:
                deviceId = items["id_device"]
                if deviceId in list_id_filter:
                    self.update_device_info(dict_device, deviceId, items, currentTime)
            # Convert dictionary to list
            message_log_file = list(dict_device.values())
            return message_log_file
        except Exception as err:
            print(f"processGetMessageAllDeviceCreateListDeviceLogFile : '{err}'")
            return None
    def update_device_info(self, dictionary, deviceId, items, currentTime):
        status_device = items["status_device"]
        status_register = items["status_register"]
        list_field = items["fields"]
        type_device = items["type_device_type"]
        device_name = items["device_name"]
        rtu_bus_address = items["rtu_bus_address"]
        point_count = items["point_count"]
        if deviceId not in dictionary:
            dictionary[deviceId] = {
                "id": int(deviceId),
                "device_name":device_name,
                "rtu_bus_address":rtu_bus_address,
                "point_id": [],
                "point_count":point_count,
                "data": [],
                "time": currentTime,
                "status_device": status_device,
                "status_register": status_register
            }
        if type_device != 1:      
            self.add_device_data(dictionary[deviceId], list_field)

    def add_device_data(self, device_info, listFieldsOfDevice):
        for field in listFieldsOfDevice:
            if field['config'] != 'MPPT':
                device_info["point_id"].append(str(field["id"]))
                dataCorrespondingfield = str(field["value"]) if field["value"] is not None else ""
                device_info["data"].append(dataCorrespondingfield)
    
    async def create_file_log(self, base_path, head_file, id_channel, typeOfFile):
        currentDateTime = datetime.datetime.strptime(get_utc(), "%Y-%m-%d %H:%M:%S")
        year, month, day = currentDateTime.year, currentDateTime.month, currentDateTime.day
        for item in self.message_log_file:
            id_device, modbus_device, point_list, data = await self.extract_device_info(item)
            
            data_in_file, directory_path, source_file ,name_file, time_file = await self.create_and_write_file(
                base_path, head_file, id_channel, typeOfFile, id_device, year, month, day, point_list, data
            )
            
            self.create_data_insert_db(
                id_device, 
                modbus_device, 
                directory_path, 
                time_file,
                source_file, 
                name_file, 
                data_in_file, 
                id_channel
            )
        if len(self.list_device_log_file) == len(self.value_insert_db):
            await self.insert_data_table_synced()

    async def extract_device_info(self, item):
        id_device = item["id"]
        modbus_device = [item['rtu_bus_address'] for item in self.message_log_file if item['id'] == id_device][0]
        point_list = [item['point_count'] for item in self.message_log_file if item['id'] == id_device][0]
        data = [item['data'] for item in self.message_log_file if item['id'] == id_device][0]
        return id_device, modbus_device, point_list, data

    async def create_and_write_file(self, base_path, head_file, id_channel, typeOfFile, id_device, year, month, day, point_list, data):
        time_file = get_utc()
        time_file_datetime = datetime.datetime.strptime(time_file, "%Y-%m-%d %H:%M:%S")
        self.time_create_file = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
        
        data_in_file_temp = self.prepare_data_in_file(data, point_list)
        directory_path = self.create_directory_path(base_path, id_channel, typeOfFile, id_device, year, month, day)
        
        try:
            file_path, source_file ,name_file = self.create_file(directory_path, head_file, id_device)
            data_in_file = await self.write_data_to_file(file_path, time_file, data_in_file_temp)
        except Exception as e:
            print(f"Error during file creation is : {e}")
        
        return data_in_file, directory_path, source_file ,name_file,time_file

    def prepare_data_in_file(self, data, point_list):
        if not data:
            return ["" for _ in range(point_list)]
        else:
            return [str(val) for val in data]

    def create_directory_path(self, base_path, id_channel, typeOfFile, id_device, year, month, day):
        directory_path = os.path.join(base_path, f"{id_channel}\\{typeOfFile}\\{id_device}\\{year}\\{month}\\{day}")
        os.makedirs(directory_path, exist_ok=True)
        return directory_path

    def create_file(self, directory_path, head_file, id_device):
        name_file = f'{head_file}-{id_device:03d}.{self.time_create_file}.log'
        file_path = os.path.join(directory_path, name_file)
        source_file = directory_path + "/" + name_file
        return file_path, source_file , name_file

    async def write_data_to_file(self, file_path, time_file, data_in_file):
        formatted_time2 = "'" + time_file + "'"
        data_in_file = f'{formatted_time2},0,0,0,{",".join(data_in_file)}'
        with open(file_path, 'w') as file:
            file.write(data_in_file)
        return data_in_file
    
    def create_data_insert_db(self, id_device, modbus_device, directory_path, time_file, source_file, name_file, data_in_file, id_channel):
        item_data_insert = (
            time_file, 
            id_device, 
            modbus_device, 
            directory_path, 
            source_file, 
            name_file, 
            get_utc(), 
            data_in_file, 
            id_channel
        )
        
        for index, item in enumerate(self.value_insert_db):
            if item[1] == id_device:
                self.value_insert_db[index] = item_data_insert
                break
        else:
            self.value_insert_db.append(item_data_insert)
            
    async def insert_data_table_synced(self):
        db_new = await DBSessionManager.get_db()
        await SyncDataService.insert_sync_data(db_new,self.value_insert_db)


