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
from dataLog.device.db_sql import *
from dbService.deviceMppt import deviceMpptService
from dbService.deviceMpptString import deviceMpptStringService
from configs.config import orm_provider as config
logger = logging.getLogger(__name__)

class LogDevice:
    def __init__(self):
        self.messageLogDevice = []  
        self.messageLogMPPTDevice = []  
class MQTTHandler(LogDevice):
    def __init__(self, log_device_instance):
        self.log_device_instance = log_device_instance
    
    async def subscribe_to_mqtt_topics(self,mqtt_service,time_interval_log_device):
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
                await self.consume_mqtt_messages(mqtt_service, client,time_interval_log_device)
                await client.stop()
        except Exception as err:
            logger.error(f"Error subscribing to MQTT topics: '{err}'")
    
    async def consume_mqtt_messages(self,mqtt_service, client,time_interval_log_device):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    logger.warning('Broker connection lost!')
                    break
                payload = MQTTService.gzip_decompress(mqtt_service, message.message)
                await self.handle_mqtt_message(mqtt_service,payload,time_interval_log_device)
        except Exception as err:
            logger.error(f"Error consuming MQTT messages: '{err}'")
    
    async def handle_mqtt_message(self, mqtt_service, message, time_interval_log_device):
        try:
            if message:
                self.log_device_instance.messageLogDevice = await self.create_message_device_log_db(message)
                self.log_device_instance.messageLogMPPTDevice = await self.create_message_device_mptt_log_db(message)
                await self.create_threading_push_status_log_device(mqtt_service, time_interval_log_device)
        except Exception as err:
            logger.error(f"Error handling MQTT message: '{err}'")
    
    async def create_message_device_log_db(self, message):
        arrayListDeviceLogDevice = {}
        try:
            current_time = get_utc()
            for items in message:
                deviceId = items["id_device"]
                statusDevice = items["status_device"]
                fields = items["fields"]
                nameOfDevice = items["device_name"]
                if deviceId not in arrayListDeviceLogDevice:
                    arrayListDeviceLogDevice[deviceId] = {
                        "id": int(deviceId),
                        "device_name": nameOfDevice,
                        "point_id": [],
                        "data": [],
                        "namekey": [],
                        "time": current_time,
                        "status_device": statusDevice,
                    }
                if items["type_device_type"] != 1:      
                    for field in fields:
                        if field['config'] != 'MPPT':
                            arrayListDeviceLogDevice[deviceId]["point_id"].append(str(field["id"]))
                            dataCorrespondingfield = str(field["value"]) if field["value"] is not None else 0.0
                            arrayListDeviceLogDevice[deviceId]["data"].append(dataCorrespondingfield)
                            arrayListDeviceLogDevice[deviceId]["namekey"].append(field["point_key"])
            result = list(arrayListDeviceLogDevice.values())
            return result
        except Exception as err:
            logger.error(f"process_message_result_list : '{err}'")
    
    async def create_message_device_mptt_log_db(self, message):
        dictionaryInforEachOfDevice = {}
        try:
            for items in message:
                deviceId = items["id_device"]
                fields = items["fields"]
                strNameDeviceType = items["name_device_type"]
                strTypeOfDevice = items["type_device_type"]
                if strTypeOfDevice != 1 and strNameDeviceType == "PV System Inverter":      
                    for field in fields:
                        if field['config'] == 'MPPT':
                            MPPTVolt = field['value']['mppt_volt']
                            MPPTAmps = field['value']["mppt_amps"]
                            MPPTpoint_key_strings = field['value']["mppt_string"]
                            MPPTpoint_key = field['point_key']
                            for item_string in MPPTpoint_key_strings:
                                MPPTpoint_key_string = item_string['point_key']
                            key_mppt = (int(deviceId), MPPTpoint_key, MPPTpoint_key_string)
                            if key_mppt in dictionaryInforEachOfDevice:
                                dictionaryInforEachOfDevice[key_mppt]['MPPTVolt'] = MPPTVolt
                                dictionaryInforEachOfDevice[key_mppt]['MPPTAmps'] = MPPTAmps
                            else:
                                dictionaryInforEachOfDevice[key_mppt] = {
                                    "id": int(deviceId),
                                    "point_key": MPPTpoint_key,
                                    "point_key_string": MPPTpoint_key_string,
                                    "MPPTVolt": MPPTVolt,
                                    "MPPTAmps": MPPTAmps
                                }
            messageLogMPPTDevice = list(dictionaryInforEachOfDevice.values())
            return messageLogMPPTDevice
        except Exception as err:
            logger.error(f"create_message_device_mptt_log_db error: '{err}'")
            
    async def create_threading_push_status_log_device(self, mqtt_service, timeLog):
        tasks = []
        if self.log_device_instance.messageLogDevice:
            for item in self.log_device_instance.messageLogDevice:
                sql_id = item["id"]
                task = self.message_status_log_device(mqtt_service, timeLog, sql_id)
                tasks.append(task)
            await asyncio.gather(*tasks)

    async def message_status_log_device(self, mqtt_service, timeLog, IdDeviceGetListMQTT):
        arrayDataOfDevice = []
        topic = ""
        strSqlID = ""
        gStrNameOfDevice = ""
        DictID = [item for item in self.log_device_instance.messageLogDevice if item["id"] == IdDeviceGetListMQTT]
        if DictID:
            arrayDataOfDevice = DictID[0]["data"]
        try:
            message_status_log_device = {
                "id_device": IdDeviceGetListMQTT,
                "time_stamp": get_utc(),
                "time_log": timeLog,
                "data_log": arrayDataOfDevice,
            }
            
            strSqlID = str(IdDeviceGetListMQTT)
            gStrNameOfDevice = [item['device_name'] for item in self.log_device_instance.messageLogDevice if item['id'] == IdDeviceGetListMQTT][0] 
            topic = "/" + "LogDevice" + "/" + strSqlID + "|" + gStrNameOfDevice
            
            MQTTService.push_data_zip(mqtt_service, topic, message_status_log_device)
        except Exception as err:
            logger.error('Error processFeedbackStatusLogDeviceSentMqttEachDevice: ', err)
class LogAllDevice(LogDevice):
    def __init__(self, log_device_instance):
        self.log_device_instance = log_device_instance
        
    async def insert_list_device_data(self):
        timeCurrent = get_utc()
        value_insert_db = []
        if self.log_device_instance.messageLogDevice:
            for item in self.log_device_instance.messageLogDevice:
                deviceId = item["id"]
                queries = await self.create_data_insert_db(timeCurrent,deviceId, self.log_device_instance.messageLogDevice)
                value_insert_db.append(queries)
        if len(value_insert_db) == len(self.log_device_instance.messageLogDevice):
            insert_data_table_device(value_insert_db)
            
    async def create_data_insert_db(self, timeCurrent,IdDeviceFromListMQTTAll, resultListDevice):
        queries = {}
        converted_queries = {}
        arrayDataUsingLogDB = []
        arrayFieldOfDevice = []
        DictID = [item for item in resultListDevice if item["id"] == IdDeviceFromListMQTTAll]
        if DictID:
            arrayDataUsingLogDB = DictID[0]["data"]
            arrayFieldOfDevice = DictID[0]["namekey"]
            statusDevice = DictID[0]["status_device"]
        if not arrayDataUsingLogDB: 
            arrayDataUsingLogDB = [None] * len(arrayFieldOfDevice)
        errorCode = 139 if statusDevice == "offline" else 0
        try:
            ValueInsertInDB = (timeCurrent, IdDeviceFromListMQTTAll,errorCode) + tuple(arrayDataUsingLogDB)
            ValueInsertInDB = tuple("0.0" if x == "" else x for x in ValueInsertInDB)
            columns = ["time", "id_device","error"] + arrayFieldOfDevice
            tableNameDeviceInDB = f"dev_{IdDeviceFromListMQTTAll}"
            queryInsertDataDeviceInDB = f"INSERT INTO {tableNameDeviceInDB} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            queries[IdDeviceFromListMQTTAll] = [queryInsertDataDeviceInDB, ValueInsertInDB]
            # conver list queries to dic converted_queries
            sql, values = queries[IdDeviceFromListMQTTAll]
            converted_queries = {
            'sql': sql,
            'values': [values] 
            }
            return converted_queries
        except Exception as e:
            logger.error(f"Error during file creation is : {e}")
            return None
class LogMPTTDevice(LogDevice):
    def __init__(self, log_device_instance):
        self.log_device_instance = log_device_instance
        
    async def insert_list_device_mptt_data(self):
        try:
            if self.log_device_instance.messageLogMPPTDevice:
                data_device_mptt, data_device_mptt_string = await self.create_data_insert_db(self.log_device_instance.messageLogMPPTDevice)
                await self.update_data_in_db(data_device_mptt, data_device_mptt_string)
        except Exception as e:
            logger.error(f"Error during data insertion: {e}")
            
    async def create_data_insert_db(self, messageLogMPPTDevice):
        data_device_mptt = []
        data_device_mptt_string = []
        for item in messageLogMPPTDevice:
            if all(key in item for key in ['id', 'point_key', 'point_key_string', 'MPPTVolt', 'MPPTAmps']):
                deviceId = item['id']
                MPPTKey = item['point_key']
                MPPTKey_string = item['point_key_string']
                voltageDeviceMPTT = item['MPPTVolt']
                currentDeviceMPTT = item['MPPTAmps']
                data_device_mptt.append((voltageDeviceMPTT, currentDeviceMPTT, deviceId, MPPTKey))
                data_device_mptt_string.append((currentDeviceMPTT, deviceId, MPPTKey_string))
        return data_device_mptt, data_device_mptt_string

    async def update_data_in_db(self, data_device_mptt, data_device_mptt_string):
        db_new = await config.get_db()
        for voltage, current, deviceId, MPPTKey in data_device_mptt:
            await deviceMpptService.updateDeviceMPPT(db_new, voltage, current, deviceId, MPPTKey)
        for current, deviceId, MPPTKey_string in data_device_mptt_string:
            await deviceMpptStringService.updateDeviceMPPTString(db_new, current, deviceId, MPPTKey_string)