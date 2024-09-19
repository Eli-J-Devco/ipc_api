# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import asyncio
import requests
import logging
sys.stdout.reconfigure(encoding='utf-8')
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import SyncSetting
from configs.config import orm_provider as config
from utils.MQTTService import *
from utils.libTime import *
from dbService.syncData import SyncDataService
from dbService.deviceList import deviceListService
from dbService.uploadChannel import UploadChannelService
from dbService.pointList import PointListService
logger = logging.getLogger(__name__)
class SyncData:
    def __init__(self):
        self.message_log_file = []  
        self.list_device_log_file = []  
        self.serial = ""
        self.number_file = ""
        self.files = ""

        self.url_handler = URL(self)
        self.file_log_handler = FileLog(self)
        self.ftp_handler = FTP(self)
        
    async def get_type_of_file(self, IdChannel):
        db_new = await config.get_db()
        typeOfFile = await UploadChannelService.select_type_log_file(db_new, IdChannel)
        return typeOfFile
    
    def get_cycle_sync(self,time_sync,time_log):
        if time_sync == 95:
            time_interval = 12
        elif time_sync == 96 :
            time_interval = 8 
        elif time_sync == 97:
            time_interval = time_log
        elif time_sync == 98:
            time_sync = 15
        elif time_sync == 99 :
            time_interval = 1
        return time_interval
    
    async def process_sync_file_log_to_stagging(self,IdChannel,typeOfFile):
        Sync_Setting = SyncSetting()
        self.number_file = await self.check_number_file_remainder(IdChannel)
        result = await self.check_url(IdChannel) 
        self.files = await self.check_sync_file_multi_or_single()
        row = 1
        if self.files == 1 :
            row = Sync_Setting.Number_File_Sync_Max
        await self.process_sync_file(IdChannel,result.uploadurl,typeOfFile,row)
        
    async def check_number_file_remainder(self,IdChannel):
        syncDataService = SyncDataService()
        db_new = await config.get_db()
        result  = await syncDataService.count_remaining_files(db_new, IdChannel)
        return result
    
    async def check_url(self,IdChannel):
        uploadChannelService = UploadChannelService()
        db_new = await config.get_db()
        result = await uploadChannelService.get_upload_url_by_id(db_new, IdChannel)
        return result
    
    async def check_sync_file_multi_or_single(self):
        files = 0
        if self.number_file > len(self.list_device_log_file)*2:
            files = 1
        return files
    
    async def process_sync_file(self,IdChannel,url,typeOfFile,row):
        syncDataService = SyncDataService()
        Sync_Setting = SyncSetting()
        db_new = await config.get_db()
        if self.list_device_log_file:
            for item in self.list_device_log_file:
                sql_id = item.id
                result = await syncDataService.select_number_row_send_cloud(db_new,IdChannel,sql_id,row)
                if result:
                    if typeOfFile == Sync_Setting.Name_Key_File_Log:
                        headers , files ,id_time = await self.file_log_handler.create_headers(result)
                        response = self.file_log_handler.post_request_log_to_cloud(headers,files,url)
                        await self.file_log_handler.update_reponse_logfile_to_db(response,IdChannel,sql_id,id_time)
                    elif typeOfFile == Sync_Setting.Name_Key_URL:
                        arrayjson,array_id_time = await self.url_handler.create_json(result,IdChannel,sql_id)
                        response = self.url_handler.post_request_json_to_cloud(arrayjson,url)
                        await self.url_handler.update_reponse_json_to_db(response,IdChannel,sql_id,array_id_time)
                    elif typeOfFile == Sync_Setting.Name_Key_Ftp:
                        soucre,id_time = await self.ftp_handler.create_source(result)
                        response = self.ftp_handler.post_request_to_FTPcloud(soucre,url)
                        await self.ftp_handler.update_reponse_ftp_to_db(response,IdChannel,sql_id,id_time)
class MQTTHandler1(SyncData):
    def __init__(self, sync_data_instance):
        self.sync_data_instance = sync_data_instance
    
    async def subscribe_to_mqtt_topics(self,mqtt_service,time_interval_log_device,IdChannel,typeOfFile,serial):
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
                await self.consume_mqtt_messages(mqtt_service, client,time_interval_log_device,IdChannel,typeOfFile,serial)
                await client.stop()
        except Exception as err:
            logger.error(f"Error subscribing to MQTT topics: '{err}'")

    async def consume_mqtt_messages(self,mqtt_service, client,time_interval_log_device,IdChannel,typeOfFile,serial):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    logger.info('Broker connection lost!')
                    break
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service,payload,time_interval_log_device,IdChannel,typeOfFile,serial)
        except Exception as err:
            logger.error(f"Error consuming MQTT messages: '{err}'")
            
    async def handle_mqtt_message(self, mqtt_service,message, time_interval_log_device,IdChannel,typeOfFile,serial):
        try:
            if message:
                await self.create_threading_push_status_log_device(mqtt_service, time_interval_log_device,IdChannel,typeOfFile)
                self.sync_data_instance.serial = serial
                if self.sync_data_instance.list_device_log_file:
                    self.sync_data_instance.message_log_file = await self.create_message_log_file(message)
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")
            
    async def create_threading_push_status_log_device(self, mqtt_service, timeLog,IdChannel,typeOfFile):
        db_new = await config.get_db()
        tasks = []
        self.sync_data_instance.list_device_log_file = await deviceListService.selectDevicesByUploadChannelID(db_new,IdChannel)
        if self.sync_data_instance.list_device_log_file:
            for item in self.sync_data_instance.list_device_log_file:
                sql_id = item.id
                task = self.push_status_log_file(mqtt_service, timeLog, sql_id,IdChannel,typeOfFile)
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def push_status_log_file(self, mqtt_service, timeLog, IdDeviceGetListMQTT, IdChannel,typeOfFile):
        topic = ""
        message = ""
        try:
            topic = await self.create_topic(IdChannel, typeOfFile, IdDeviceGetListMQTT)
            message = await self.create_message(IdDeviceGetListMQTT,timeLog)
            if topic and message :
                MQTTService.push_data_zip(mqtt_service, topic, message)
        except Exception as err:
            logger.error('Error processFeedbackStatusLogDeviceSentMqttEachDevice: ', err)

    async def create_topic(self, IdChannel, typeOfFile, IdDeviceGetListMQTT):
        strSqlID = str(IdDeviceGetListMQTT)
        device_names = [item["device_name"] for item in self.sync_data_instance.message_log_file if item["id"] == IdDeviceGetListMQTT]
        topic = f"/Updata/Channel{IdChannel}|{typeOfFile}/{strSqlID}|{device_names}"
        return topic
    
    async def create_message(self ,IdDevice, timeLog):
        if self.sync_data_instance.files == 0:
            status_file = "single"
        else:
            status_file = "multi"
        message = {
            "time_stamp": get_utc(),
            "id_device": IdDevice,
            "status_file": status_file,
            "remainder_all_file": self.sync_data_instance.number_file,
            "time_sync" : timeLog,
        }
        return message

    async def create_message_log_file(self, messageAllDevice):
        dict_device = {}
        list_id_filter = {item.id for item in self.sync_data_instance.list_device_log_file}
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
            logger.error(f"processGetMessageAllDeviceCreateListDeviceLogFile : '{err}'")
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
class URL(SyncData):
    def __init__(self, sync_data_instance):
        self.sync_data_instance = sync_data_instance
        
    async def create_json(self,result,IdChannel,sqlid):
        pointListService = PointListService()
        db_new = await config.get_db()
        arrayjson = []
        id_times = []
        result_id_pointkey = await pointListService.select_point_keys_by_deviceid(db_new,sqlid)
        for item in result:
            id_times.append(item.id)
            array_file = await self.read_data_file(item.filename, item.source)
            if array_file :
                jsondata = {
                    'id_channel': IdChannel,
                    'id_device': item.id_device,
                    'serial_number_port': self.sync_data_instance.serial,
                    'datetime': get_utc(),
                    'datas': {
                            "time": array_file[0] if len(array_file) > 0 else None,
                            "error": array_file[1] if len(array_file) > 1 else None,
                            "high_alarm": array_file[2] if len(array_file) > 2 else None,
                            "low_alarm": array_file[3] if len(array_file) > 3 else None
                            }
                            }
                for i in range(4, len(array_file)):
                    if i - 4 < len(result_id_pointkey):
                        key = result_id_pointkey[i-4]
                        value = array_file[i] if array_file[i] else None
                        jsondata["datas"][key['id_pointkey']] = value
                arrayjson.append(jsondata)
        return arrayjson,id_times

    async def read_data_file(self,file_name,source):
        if file_name and os.path.exists(source):
            with open(source, 'r') as file:
                file_content = file.read()
                array_file = file_content.split(',')
        return array_file
    
    def post_request_json_to_cloud(self,arrayjson,url):
        for json in arrayjson:
            response = requests.post(url,json=json) 
        return response.status_code
        
    async def update_reponse_json_to_db(self,response,IdChannel,sql_id,id_time):
        syncDataService = SyncDataService()
        db_new = await config.get_db()
        if response == 200:
            for id in id_time:
                result = await syncDataService.delete_synced_data(db_new, id, IdChannel, sql_id)
                logger.info(f"Deleted synced data for time: {id} with id {sql_id} and delete {result}")
        else:
            number_time_rety = await syncDataService.update_number_of_time_retry(db_new,id,IdChannel,sql_id)
            logger.info(f"Updated number retry:{number_time_rety}")
            if number_time_rety == 5 :
                result = await syncDataService.update_error_status(db_new, id, IdChannel, sql_id)
            logger.info(f"Updated error status for time: {id} with id {sql_id} number retry: {number_time_rety}")
class FileLog(SyncData):
    def __init__(self, sync_data_instance):
        self.sync_data_instance = sync_data_instance
    
    async def create_headers(self,result):
        first_item = result[0]
        files = []
        id_times = []
        headers = {
            'SERIALNUMBER': self.sync_data_instance.serial,
            'MODBUSDEVICE': first_item.modbusdevice,
            'MODBUSPORT': first_item.modbusport,
            'MODE': 'LOGFILEUPLOAD'
        }
        for item in result:
            id_time = item.id
            id_times.append(id_time)
            file = ('LOGFILE', (item.filename, open(item.source, 'rb'), 'text/plain'))
            files.append(file)
        return headers , files ,id_times
    
    def post_request_log_to_cloud(self,headers,files,url):
        if files:
            response = requests.post(url, files=files , data=headers)
            return response.text

    async def update_reponse_logfile_to_db(self,response,IdChannel,sql_id,id_time):
        syncDataService = SyncDataService()
        db_new = await config.get_db()
        if response == "\nSUCCESS\n":
            for id in id_time:
                result = await syncDataService.delete_synced_data(db_new, id, IdChannel, sql_id)
                logger.info(f"Deleted synced data for time: {id} with id {sql_id} and delete {result}")
        else:
            for id in id_time:
                number_time_rety = await syncDataService.update_number_of_time_retry(db_new,id,IdChannel,sql_id)
                logger.info(f"Updated number retry:{number_time_rety}")
                if number_time_rety == 5 :
                    result = await syncDataService.update_error_status(db_new, id, IdChannel, sql_id)
                logger.info(f"Updated error status for time: {id} with id {sql_id} number retry: {number_time_rety}")
class FTP(SyncData):
    def __init__(self, sync_data_instance):
        self.sync_data_instance = sync_data_instance
    
    async def create_source(self,result):
        first_item = result[0]
        files = []
        id_times = []
        source = {
            'SERIALNUMBER': self.sync_data_instance.serial,
            'MODBUSDEVICE': first_item.modbusdevice,
            'MODBUSPORT': first_item.modbusport,
            'MODE': 'LOGFILEUPLOAD'
        }
        for item in result:
            id_time = item.id
            id_times.append(id_time)
            file = ('LOGFILE', (item.filename, open(item.source, 'rb'), 'text/plain'))
            files.append(file)
        return source,id_times
    
    def post_request_to_FTPcloud(self,json,url):
        if json :
            response = requests.post(url,json=json) 
            return response.status_code
    
    async def update_reponse_ftp_to_db(self,response,IdChannel,sql_id,id_time):
        syncDataService = SyncDataService()
        db_new = await config.get_db()
        if response == True:
            for id in id_time:
                result = await syncDataService.delete_synced_data(db_new, id, IdChannel, sql_id)
                logger.info(f"Deleted synced data for time: {id} with id {sql_id} and delete {result}")
        else:
            for id in id_time:
                number_time_rety = await syncDataService.update_number_of_time_retry(db_new,id,IdChannel,sql_id)
                logger.info(f"Updated number retry:{number_time_rety}")
                if number_time_rety == 5 :
                    result = await syncDataService.update_error_status(db_new, id, IdChannel, sql_id)
                logger.info(f"Updated error status for time: {id} with id {sql_id} number retry: {number_time_rety}")
