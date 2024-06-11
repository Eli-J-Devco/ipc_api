# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import ipaddress
import json
import os
import signal
import subprocess
import sys
from pprint import pprint
from typing import Annotated, Optional, Union

import mqttools

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
sys.stdout.reconfigure(encoding='utf-8')
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

# 
from configs.config import Config
from configs.config import orm_provider as db_config
# 
# from database.db import get_db
from utils.libCom import cov_xml_sql, get_mybatis
from utils.libMySQL import *
from utils.logger_manager import setup_logger
from utils.mqttManager import mqtt_public, mqtt_public_common, mqttService
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC 
# IPC/Init/API/Requests
# IPC/Init/API/Responses
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
from dataclasses import asdict, dataclass

# from api.domain.sld_group.sld_group_model import (SldGroupBase,
#                                                   SldGroupResponse,
#                                                   SldGroupUpdate)
# import api.domain.deviceGroup.models as deviceGroup_models
# import api.domain.deviceList.models as deviceList_models
# import api.domain.project.models as project_models
# import api.domain.template.models as template_models
# import api.domain.user.models as user_models
# import model.models as models
from apiGateway.devices import devices_service
from apiGateway.project_setup import project_service
from apiGateway.rs485 import rs485_service
from apiGateway.single_line_diagram import single_line_service
from apiGateway.template import template_service
from apiGateway.upload_channel import upload_channel_service


# ----------------- API
# ----------------- APIGateway
# ----------------- Dev
# ----------------- LogDevice
    # cron job device  According to time
# ----------------- LogFile
    # create file device According to channel
# ----------------- MQTTControl
    # 
# ----------------- UpData
    # upData According to channel
def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
class apiGateway:
    def __init__(self,
                SERIAL_NUMBER,
                MQTT_BROKER="127.0.0.1",
                MQTT_PORT=1883,
                MQTT_USERNAME="",
                MQTT_PASSWORD="",
                        **kwargs):
        # self.db_new =db_new
        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOPIC = SERIAL_NUMBER
        self.MQTT_USERNAME = MQTT_USERNAME
        self.MQTT_PASSWORD = MQTT_PASSWORD
        self.DeviceList=[]
    # 
    async def handle_messages_api(self,client):
        try :
            
            device_init=devices_service.DevicesService(
                            host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            password=self.MQTT_PASSWORD,
                            update_device_list=self.DeviceList)
            # 
            project_init=project_service.ProjectService()
            template_init=template_service.TemplateService()
            upload_channel_init=upload_channel_service.UploadChannelService()
            rs485_init=rs485_service.RS485Service()
            # 
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                # print(f'Topic:   {message.topic}')
                result=json.loads(message.message.decode())
                # print(f'Message: {result}')
                if 'CODE' in result.keys() and 'PAYLOAD' in result.keys():
                    match result['CODE']:
                        case "UpdateSiteInformation":
                            # {
                            #     "CODE": "UpdateSiteInformation", 
                            #     "PAYLOAD":""
                            # }
                            await project_init.init_pm2()
                        case "UpdateLoggingRate":
                            # {
                            #     "CODE": "UpdateLoggingRate", 
                            #     "PAYLOAD":""
                            # }
                            # table project
                            await project_init.init_logging_rate()
                        case "CreateTCPDev":
                            # {
                            #     "CODE": "CreateTCPDev", 
                            #     "PAYLOAD":
                            #         { 
                            #             "device":[
                            #             {
                            #                 "id":item.id,
                            #                 "name":item.name,
                            #                 "connect_type":driver_list.name,
                            #                 "id_communication":id_communication,
                            #                 "mode":item.mode
                            #             }
                            #                 ]
                            #         }
                            # }
                            new_device=result['PAYLOAD']
                            await device_init.create_dev_tcp(new_device)
                        case "CreateRS485Dev":
                            #  data of device
                            # {
                            #     "CODE": "CreateRS485Dev", 
                            #     "PAYLOAD": 
                            #         {
                            #             "id_communication":id_communication,
                            #             "device":[
                            #                 {
                            #                     "id":item.id,
                            #                     "name":item.name,
                            #                     "connect_type":driver_list.name,
                            #                     "id_communication":id_communication,
                            #                     "mode":item.mode
                            #                 }
                            #             ]
                            #         }
                            # }
                            
                            db_new=await db_config.get_db()
                            new_device=result['PAYLOAD']
                            await device_init.create_dev_rs485(new_device,db_new)
                        case "DeleteDev":
                            # data of device
                            # mode == 1:  # Disable
                            # mode == 2:  # Delete
                            # {
                            #     "CODE":"DeleteDev",
                            #     "PAYLOAD":{
                            #         "device":[
                            #             {
                            #             "mode": mode,
                            #             "id": item.id,
                            #             "name": device.name,
                            #             "id_communication": id_communication,
                            #             "connect_type": driver_name,
                            #             }
                            #             ],
                            #         "delete_mode":mode
                            #     }
                            # }
                            db_new=await db_config.get_db()
                            delete_device=result['PAYLOAD']
                            await device_init.delete_dev(delete_device,db_new)
                        case "UpdateDev":
                            # {
                            #     "CODE": "UpdateDev", 
                            #     "PAYLOAD":
                            #         { 
                            #            "id":296
                            #         }
                            # }
                            db_new=await db_config.get_db()
                            update_device=result['PAYLOAD']
                            await device_init.update_dev(update_device,db_new)
                        case "UpdateTemplate":
                            # {
                            #     "CODE": "UpdateTemplate", 
                            #     "PAYLOAD":
                            #         { 
                            #            "id":3
                            #         }
                            # }
                            db_new=await db_config.get_db()
                            update_template=result['PAYLOAD']
                            await template_init.init_pm2(update_template,db_new)
                        case "DeleteTemplate":
                            pass
                        case "UpdatePortRS485":
                            # {
                            #     "CODE": "UpdatePortRS485", 
                            #     "PAYLOAD":
                            #         { 
                            #            "id":1
                            #         }
                            # }
                            db_new=await db_config.get_db()
                            update_communication=result['PAYLOAD']
                            await rs485_init.init_pm2(update_communication,db_new)
                        case "UpdateUploadChannels":

                            # {
                            #     "CODE": "UpdateUploadChannels", 
                            #     "PAYLOAD":[
                            #               {"id":1},
                            #               {"id":2},
                            #               {"id":3}
                            #               ]
                            # }
                            
                            db_new=await db_config.get_db()
                            upload_channel_list=result['PAYLOAD']
                            await upload_channel_init.init_pm2(upload_channel_list,db_new)
        except Exception as err:
            print(f"Error handle_messages_api: '{err}'")   
    async def managerApplicationsWithPM2(self):
        try:
            
            Topic=f'{self.MQTT_TOPIC}/Init/API/Requests'
            client = mqttools.Client(host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            subscriptions=[Topic],
                            password=bytes(self.MQTT_PASSWORD, 'utf-8'),
                            connect_delays=[1, 2, 4, 8]
                            )
            LOGGER = setup_logger(module_name='apiGateway')
            LOGGER.warn(f'--- init ---')
            while True:
                await client.start()
                await self.handle_messages_api(client)
                await client.stop()
        except Exception as err:
            print(f"Error managerApplicationsWithPM2: '{err}'")   
    # 
    async def handle_messages_driver(self,client,Topic):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                result=json.loads(message.message.decode())
                for i,item in enumerate(self.DeviceList):
                    if message.topic==f'{Topic}/{item["id_device"]}':
                        if 'id_device_type' in result.keys():
                            self.DeviceList[i]["id_device_type"]=result["id_device_type"]
                        if 'name_device_type' in result.keys():
                            self.DeviceList[i]["name_device_type"]=result["name_device_type"]
                        if 'status_device' in result.keys():
                            self.DeviceList[i]["status_device"]=result["status_device"]
                        if 'timestamp' in result.keys():
                            self.DeviceList[i]["timestamp"]=result["timestamp"]
                        if 'message' in result.keys():
                            self.DeviceList[i]["message"]=result["message"]
                        if 'status_register' in result.keys():
                            self.DeviceList[i]["status_register"]=result["status_register"]
                        if 'point_count' in result.keys():
                            self.DeviceList[i]["point_count"]=result["point_count"]
                        if 'parameters' in result.keys():
                            self.DeviceList[i]["parameters"]=result["parameters"]
                        if 'fields' in result.keys():
                            self.DeviceList[i]["fields"]=result["fields"]
                        if 'mppt' in result.keys():
                            self.DeviceList[i]["mppt"]=result["mppt"]
                        if 'mode' in result.keys():
                            self.DeviceList[i]["mode"]=result["mode"]
                        if 'control_group' in result.keys():
                            self.DeviceList[i]["control_group"]=result["control_group"]
                        if 'rated_power' in result.keys():
                            self.DeviceList[i]["rated_power"]=result["rated_power"]
                        if 'rated_power_custom' in result.keys():
                            self.DeviceList[i]["rated_power_custom"]=result["rated_power_custom"]
                        if 'min_watt_in_percent' in result.keys():
                            self.DeviceList[i]["min_watt_in_percent"]=result["min_watt_in_percent"]
                        if 'meter_type' in result.keys():
                            self.DeviceList[i]["meter_type"]=result["meter_type"] 
                        if 'inverter_type' in result.keys():
                            self.DeviceList[i]["inverter_type"]=result["inverter_type"]
                        if 'parent' in result.keys():
                            self.DeviceList[i]["parent"]=result["parent"]
        except Exception as err:
            print(f"Error handle_messages_driver: '{err}'")
    async def deviceListSub(self):
        try:
            Topic=self.MQTT_TOPIC+"/"+"Devices"
            client = mqttools.Client(host=self.MQTT_BROKER, 
                                port=self.MQTT_PORT ,
                                username= self.MQTT_USERNAME, 
                                password=bytes(self.MQTT_PASSWORD, 'utf-8'),
                                subscriptions=[Topic+"/#"],
                                connect_delays=[1, 2, 4, 8]
                                )
            while True:
                await client.start()
                await self.handle_messages_driver(client,Topic)
                await client.stop()
        except Exception as err:
            print('Error MQTT deviceListSub')
    # 
    async def deviceListPub(self):
        try:
            try:
                
                db_new=await db_config.get_db()
                result= await db_new.execute(text("select * from `device_list` where `status`=1;"))
                
                result_device=[row._asdict() for row in result.all()]

                for item in result_device:
                    self.DeviceList.append({
                        "id_device":item["id"],
                        "device_name":item["name"],
                        "mode":item["mode"],
                        "parameters":[],
                        "efficiency":item["efficiency"],
                        "parent":item["parent"],
                        "inverter_type":item["inverter_type"],
                        "meter_type":item["meter_type"],
                    })
            except Exception as err:
                print('An exception occurred',err)
            finally:
                await db_new.close()
            topic=f"{self.MQTT_TOPIC}/Devices/All"
            while True:
                mqtt_data=[]
                for item in self.DeviceList:
                    parameters=[]
                    fields=[]
                    mppt=[]
                    if 'parameters' in item.keys():
                        for item_para in item["parameters"] :
                            parameter_fields=[]
                            if 'fields' in item_para.keys():
                                for item_fields in item_para["fields"]:
                                    parameter_fields.append({
                                        **item_fields,
                                        "timestamp":getUTC()
                                    })
                                parameters.append(
                                    {
                                        **item_para,
                                        "fields":parameter_fields
                                    }
                                )
                    if 'fields' in item.keys():
                        fields=[ {**item_fields,
                                  "timestamp":getUTC()
                                  } for item_fields in item["fields"]]
                    if 'mppt' in item.keys():
                        mppt=[ {**item_mppt,
                                  "timestamp":getUTC()
                                  } for item_mppt in item["mppt"]]
                    mqtt_data.append({
                        **item,
                        "timestamp":getUTC(),
                        "parameters":parameters,
                        "fields":fields,
                        "mppt":mppt
                    })

                mqtt_public_common(self.MQTT_BROKER,
                                self.MQTT_PORT,
                                topic,
                                self.MQTT_USERNAME,
                                self.MQTT_PASSWORD,
                                mqtt_data)
                await asyncio.sleep(1)
        except Exception as err:
            print('Error MQTT deviceListPub')
        finally:
            print('MQTT deviceListPub end')
    # 
    async def handle_ipc_system(self,client):
        try:
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                result=json.loads(message.message.decode())
                if 'cmd' in result.keys():
                    cmd=result['cmd']
                    match cmd:
                        case "reboot":
                            if sys.platform == 'win32':
                                # use run with window          
                                print(f'reboot ipc')
                            else:
                                # use run with ubuntu/linux
                                subprocess.Popen(
                                    f'sudo reboot', shell=True).communicate()
                    
        except Exception as err:
            print('Error MQTT handle_ipc_system')        
    async def ipc_system(self):
        try:
            Topic=self.MQTT_TOPIC+"/"+"System"
            client = mqttools.Client(host=self.MQTT_BROKER, 
                                port=self.MQTT_PORT ,
                                username= self.MQTT_USERNAME, 
                                password=bytes(self.MQTT_PASSWORD, 'utf-8'),
                                subscriptions=[Topic+"/#"],
                                connect_delays=[1, 2, 4, 8]
                                )
            while True:
                await client.start()
                await self.handle_ipc_system(client)
                await client.stop()
        except Exception as err:
            print('Error MQTT system_inform: ',err)
    # 


async def main():
    tasks = []
    db_new=await db_config.get_db()
    project_init=project_service.ProjectService()
    result=await project_init.project_inform(db_new)
    SERIAL_NUMBER=result["serial_number"]
    api_gateway=apiGateway(
                            SERIAL_NUMBER,
                            MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            )

    
    
    
    tasks.append(asyncio.create_task(
        api_gateway.managerApplicationsWithPM2()))
    tasks.append(asyncio.create_task(
        api_gateway.deviceListSub()))
    tasks.append(asyncio.create_task(
        api_gateway.deviceListPub()))
    tasks.append(asyncio.create_task(
        api_gateway.ipc_system()))
    # tasks.append(asyncio.create_task(
    #     api_gateway.single_line_diagram()))
    
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
        asyncio.run(main())
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(main())
    except KeyboardInterrupt:
        print ('API GATEWAY stopped.')
        sys.exit(0)
