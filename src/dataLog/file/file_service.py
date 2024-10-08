# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import asyncio
import logging
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from utils.MQTTService import *
from utils.libTime import *
from dbService.syncData import SyncDataService
from dbService.deviceList import deviceListService
from dbService.uploadChannel import UploadChannelService
from configs.config import orm_provider as config
class LogFile:
    def __init__(self,logger: logging.Logger):
        self.message_log_file = []  
        self.list_device_log_file = []  
        self.time_create_file = ""
        self.value_insert_db = []
        self.logger = logger
        
    async def get_type_of_file(self, IdChannel):
        db_new = await config.get_db()
        typeOfFile = await UploadChannelService.select_type_log_file(db_new, IdChannel)
        return typeOfFile
class MQTTHandler(LogFile):
    def __init__(self, log_file_instance):
        self.log_file_instance = log_file_instance

    async def subscribe_to_mqtt_topics(self,mqtt_service,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile):
        try:
            client = mqttools.Client(
                host=mqtt_service.host,
                port=mqtt_service.port,
                username=mqtt_service.username,
                password=bytes(mqtt_service.password, 'utf-8'),
                subscriptions=mqtt_service.topics,
                connect_delays=[1, 2, 4, 8]
            )
            while True :
                await client.start()
                await self.consume_mqtt_messages(mqtt_service, client,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile)
                await client.stop()
        except Exception as err:
            self.log_file_instance.logger.error(f"Error subscribing to MQTT topics: '{err}'")
    
    async def consume_mqtt_messages(self,mqtt_service, client,time_interval_log_device,log_file_instance,IdChannel,Head_File_Log,typeOfFile):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    self.log_file_instance.logger.info('Broker connection lost!')
                    break
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service,payload,time_interval_log_device,IdChannel,Head_File_Log,typeOfFile)
        except Exception as err:
            self.log_file_instance.logger.error(f"Error consuming MQTT messages: '{err}'")
            
    async def handle_mqtt_message(self, mqtt_service, message, time_interval_log_device,IdChannel,Head_File_Log,typeOfFile):
        try:
            if message:
                await self.create_threading_push_status_log_device(mqtt_service, time_interval_log_device,IdChannel,Head_File_Log,typeOfFile)
                if self.log_file_instance.list_device_log_file:
                    self.log_file_instance.message_log_file = await self.create_message_log_file(message)
        except Exception as err:
            self.log_file_instance.logger.error(f"Error handling MQTT message: '{err}'")
    
    async def create_threading_push_status_log_device(self, mqtt_service, timeLog, IdChannel, Head_File_Log, typeOfFile):
        db_new = await config.get_db()
        tasks = []
        self.log_file_instance.list_device_log_file = await deviceListService.selectDevicesByUploadChannelID(db_new, IdChannel)
        if self.log_file_instance.list_device_log_file:
            for item in self.log_file_instance.list_device_log_file:
                sql_id = item.id 
                task = self.push_status_log_file(mqtt_service, timeLog, sql_id, IdChannel, Head_File_Log, typeOfFile)
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
        except Exception as err:
            self.log_file_instance.logger.error(f"Error in push status log file for device ID '{IdDeviceGetListMQTT}', channel '{IdChannel}': {err}. Topic: '{topic}', Message: '{message}'")

    async def create_topic(self, IdChannel, typeOfFile, IdDeviceGetListMQTT):
        strSqlID = str(IdDeviceGetListMQTT)
        gStrNameOfDevice = [item["device_name"] for item in self.log_file_instance.message_log_file if item["id"] == IdDeviceGetListMQTT][0]
        topic = f"/LogFile/Channel{IdChannel}|{typeOfFile}/{strSqlID}|{gStrNameOfDevice}"
        return topic
    
    async def create_message(self ,IdDevice, Head_File_Log, timeLog):
        DictID = [item for item in self.log_file_instance.message_log_file if item["id"] == IdDevice]
        if DictID:
            data = DictID[0]["data"]
            status_device = DictID[0]["status_device"]
            message = {
                "time_stamp": get_utc(),
                "id_device": IdDevice,
                "name_file": f'{Head_File_Log}-{IdDevice:03d}.{self.log_file_instance.time_create_file}.log',
                "status_device": status_device,
                "time_log": timeLog,
                "data_log": data,
            }
            return message
        return None
    
    async def create_message_log_file(self, messageAllDevice):
        dict_device = {}
        list_id_filter = {item.id for item in self.log_file_instance.list_device_log_file}
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
            self.log_file_instance.logger.error(f"Error in create message log file: {err}.")
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
class ProcessLogFile(LogFile):
    def __init__(self, log_file_instance):
        self.log_file_instance = log_file_instance
        
    async def create_file_log(self, base_path, head_file, id_channel, typeOfFile):
        currentDateTime = datetime.datetime.strptime(get_utc(), "%Y-%m-%d %H:%M:%S")
        year, month, day = currentDateTime.year, currentDateTime.month, currentDateTime.day
        for item in self.log_file_instance.message_log_file:
            try:
                id_device, modbus_device, point_list, data = await self.extract_device_info(item)
                data_in_file, directory_path, source_file ,name_file, time_file = await self.create_and_write_file(
                    base_path, head_file, id_channel, typeOfFile, id_device, year, month, day, point_list, data)
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
            except Exception as err:
                self.log_file_instance.logger.error(f"Error processing device ID '{item['id']}': {err}")
                
        if len(self.log_file_instance.list_device_log_file) == len(self.log_file_instance.value_insert_db):
            await self.insert_data_table_synced()

    async def extract_device_info(self, item):
        try:
            id_device = item["id"]
            modbus_device = [item["rtu_bus_address"] for item in self.log_file_instance.message_log_file if item["id"] == id_device][0]
            point_list = [item["point_count"] for item in self.log_file_instance.message_log_file if item["id"] == id_device][0]
            data = [item["data"] for item in self.log_file_instance.message_log_file if item["id"] == id_device][0]
            return id_device, modbus_device, point_list, data
        except Exception as err:
            self.log_file_instance.logger.error(f"Error extracting device info for item '{item}': {err}")
            return None, None, None, None

    async def create_and_write_file(self, base_path, head_file, id_channel, typeOfFile, id_device, year, month, day, point_list, data):
        time_file = get_utc()
        time_file_datetime = datetime.datetime.strptime(time_file, "%Y-%m-%d %H:%M:%S")
        self.log_file_instance.time_create_file = time_file_datetime.strftime("%Y%m%d%H%M%S").replace(":", "")
        data_in_file_temp = self.prepare_data_in_file(data, point_list)
        directory_path = self.create_directory_path(base_path, id_channel, typeOfFile, id_device, year, month, day)
        try:
            file_path, source_file, name_file = self.create_file(directory_path, head_file, id_device)
            data_in_file = await self.write_data_to_file(file_path, time_file, data_in_file_temp)
            return data_in_file, directory_path, source_file, name_file, time_file
        except Exception as e:
            self.log_file_instance.logger.error(f"Error during file creation for device ID '{id_device}': {e}")
            return None, None, None, None, None

    def prepare_data_in_file(self, data, point_list):
        if not data:
            return ["" for _ in range(point_list)]
        else:
            return [str(val) for val in data]

    def create_directory_path(self, base_path, id_channel, typeOfFile, id_device, year, month, day):
        directory_path = os.path.join(base_path, f"{id_channel}/{typeOfFile}/{id_device}/{year}/{month}/{day}")
        try:
            os.makedirs(directory_path, exist_ok=True)
            return directory_path
        except Exception as err:
            self.log_file_instance.logger.error(f"Error creating directory path '{directory_path}': {err}")
            return None

    def create_file(self, directory_path, head_file, id_device):
        if not head_file or id_device is None:
            self.log_file_instance.logger.error("File name is incomplete. Please check the inputs.")
            return None, None, None
        name_file = f'{head_file}-{id_device:03d}.{self.log_file_instance.time_create_file}.log'
        try : 
            file_path = os.path.join(directory_path, name_file)
            source_file = directory_path + "/" + name_file
            return file_path, source_file , name_file
        except Exception as e:
            self.log_file_instance.logger.error(f"Error creating file '{file_path}': {e}")
            return None , None , None
        
    async def write_data_to_file(self, file_path, time_file, data_in_file):
        if not data_in_file or len(data_in_file) == 0:
            self.log_file_instance.logger.error("Data to write is empty. Please provide valid data.")
            return None
        formatted_time2 = "'" + time_file + "'"
        data_in_file = f'{formatted_time2},0,0,0,{",".join(data_in_file)}'
        try:
            with open(file_path, 'w') as file:
                file.write(data_in_file)
            return data_in_file
        except Exception as e:
            self.log_file_instance.logger.error(f"Error writing data to file '{file_path}': {e}")
            return None
    
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
        
        try:
            for index, item in enumerate(self.log_file_instance.value_insert_db):
                if item[1] == id_device:
                    self.log_file_instance.value_insert_db[index] = item_data_insert
                    break
            else:
                self.log_file_instance.value_insert_db.append(item_data_insert)
        except Exception as err:
            self.log_file_instance.logger.error(f"Error creating data insert for device ID '{id_device}': {err}")
            
    async def insert_data_table_synced(self):
        try:
            db_new = await config.get_db()
            await SyncDataService.insert_sync_data(db_new, self.log_file_instance.value_insert_db)
        except Exception as err:
            self.log_file_instance.logger.error(f"Error inserting synced data into database: {err}")

