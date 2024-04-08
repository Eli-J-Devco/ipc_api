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

from configs.config import Config
from database.db import get_db
from utils.libCom import cov_xml_sql, get_mybatis
from utils.libMySQL import *
from utils.mqttManager import mqtt_public, mqtt_public_common
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
import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.project.models as project_models
import api.domain.template.models as template_models
import api.domain.user.models as user_models
import model.models as models


def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
class apiGateway:
    def __init__(self,MQTT_BROKER="127.0.0.1",
                        MQTT_PORT=1883,
                        MQTT_TOPIC="",
                        MQTT_USERNAME="",
                        MQTT_PASSWORD="",
                        MQTT_BROKER_CLOUD="127.0.0.1",
                        MQTT_PORT_CLOUD=1883,
                        MQTT_TOPIC_CLOUD="",
                        MQTT_USERNAME_CLOUD="",
                        MQTT_PASSWORD_CLOUD=""
                        ):
        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOPIC = MQTT_TOPIC
        self.MQTT_USERNAME = MQTT_USERNAME
        self.MQTT_PASSWORD = MQTT_PASSWORD
        self.DeviceList=[]
        
        self.MQTT_BROKER_CLOUD = MQTT_BROKER_CLOUD
        self.MQTT_PORT_CLOUD = MQTT_PORT_CLOUD
        self.MQTT_TOPIC_CLOUD = MQTT_TOPIC_CLOUD
        self.MQTT_USERNAME_CLOUD = MQTT_USERNAME_CLOUD
        self.MQTT_PASSWORD_CLOUD = MQTT_PASSWORD_CLOUD
        
        
    async def managerApplicationsWithPM2(self):
        try:
            
            Topic=f'{self.MQTT_TOPIC}/Init/API/Requests'
            client = mqttools.Client(host=self.MQTT_BROKER, 
                            port=self.MQTT_PORT,
                            username= self.MQTT_USERNAME, 
                            password=bytes(self.MQTT_PASSWORD, 'utf-8'))
            await client.start()
            await client.subscribe(Topic)
            while True:
                message = await client.messages.get()

                if message is None:
                    print('Broker connection lost!')
                    break
                # print(f'Topic:   {message.topic}')
                result=json.loads(message.message.decode())
                # print(f'Message: {result}')
                if 'CODE' in result.keys() and 'PAYLOAD' in result.keys():
                    db=get_db()
                    match result['CODE']:
                        case "CreateTCPDev":
                            new_device=result['PAYLOAD']
                            print(new_device[0])
                            #  init start pm2 new app
                            for item in new_device:
                                
                                pid = f'Dev|{item["id_com"]}|{item["connect_type"]}|{item["id"]}|{item["name"]}'
                                await create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,item["id"])
                            # restart pm2 app log
                            pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                            result=await restart_program_pm2_many(pm2_app_list)
                            # 
                            now = datetime.datetime.now(
                            datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                            param=  {
                                        "CODE":"CreateTCPDev",
                                        "PAYLOAD":new_device,
                                        "TIME_STAMP":now
                                    }
                            mqtt_public("/Init/API/Responses",param)
                        case "CreateRS485Dev":
                            id_communication=result['PAYLOAD']
                            result_find_app_pm2=await find_program_pm2(f'Dev|{str(id_communication)}|')
                            if result_find_app_pm2==100:
                                result_delete_app_pm2=await delete_program_pm2(f'Dev|{str(id_communication)}|') 
                                device_list_query = db.query(
                                            deviceList_models.Device_list).filter(
                                            deviceList_models.Device_list.id_communication ==
                                                                        id_communication).filter(
                                            deviceList_models.Device_list.status == 1).order_by(
                                                                        deviceList_models.Device_list.id.asc()).all()
                                db.commit()
                                # check device same group rs485 com port   
                                item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                                id_communication]
                                if item_rs485:
                                    # check group rs485 same com port

                                    sql_query_select_device= cov_xml_sql("deviceConfig.xml","select_all_device",
                                                                            {"id_communication":id_communication})
                                    result_device_group_rs485 = db.execute(
                                                                        text(sql_query_select_device), 
                                                                            ).all()
                                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]  
                                    db.close()                                          
                                    # init restart pm2 app same rs485
                                    await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                    # restart pm2 app log
                                    pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                                    await restart_program_pm2_many(pm2_app_list) 
                            elif result_find_app_pm2!=100:
                                print('---------- create group RS485 same com port when list device empty ----------')
                                # check group rs485 same com port
                                sql_query_select_device= cov_xml_sql("deviceConfig.xml","select_all_device",
                                                                        {"id_communication":id_communication})
                                result_device_group_rs485 =  db.execute(
                                                                        text(sql_query_select_device), 
                                                                            ).all()
                                results_device_group_dict = [row._asdict() for row in result_device_group_rs485] 
                                db.close()                                                       
                                # init restart pm2 app same rs485
                                await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                # restart pm2 app log
                                pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                                result=await restart_program_pm2_many(pm2_app_list)
                            else:
                                pass
                            now = datetime.datetime.now(
                            datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                            param=  {
                                        "CODE":"CreateRS485Dev",
                                        "PAYLOAD":id_communication,
                                        "TIME_STAMP":now
                                    }
                            mqtt_public("/Init/API/Responses",param)
                        case "DeleteDev":
                            device=result['PAYLOAD']
                            device_tcp=[]
                            device_rs485=[]
                            communication_list=[]
                            
                            for item in device:
                                if item["driver_name"]=="RS485":
                                    # id_communication=item['id_communication']
                                    communication_list.append(item['id_communication'])
                                elif item["driver_name"]=="Modbus/TCP":
                                    device_tcp.append(f'Dev|{item["id_communication"]}|Modbus/TCP|{item["id"]}')
                                    
                            if device_tcp:
                                await delete_program_pm2_many(device_tcp)
                                # restart pm2 app log
                                pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                                result=await restart_program_pm2_many(pm2_app_list)
                            if communication_list:
                                device_rs485=list(set(communication_list))
                            # if device_rs485:
                            #     for item in device_rs485:
                            #         result_find_app_pm2=await find_program_pm2(f'Dev|{str(id_communication)}|')
                            #         if result_find_app_pm2==100:
                            #             result_delete_app_pm2=await delete_program_pm2(f'Dev|{str(id_communication)}|') 
                            #             device_list_query = db.query(
                            #                         deviceList_models.Device_list).filter(
                            #                         deviceList_models.Device_list.id_communication ==
                            #                                                     id_communication).filter(
                            #                         deviceList_models.Device_list.status == 1).order_by(
                            #                                                     deviceList_models.Device_list.id.asc()).all()
                            #             db.commit()
                            #             # check device same group rs485 com port   
                            #             item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                            #                             id_communication]
                            #             if item_rs485:
                            #                 # check group rs485 same com port

                            #                 sql_query_select_device= cov_xml_sql("deviceConfig.xml","select_all_device",
                            #                                                         {"id_communication":id_communication})
                            #                 result_device_group_rs485 = db.execute(
                            #                                                     text(sql_query_select_device), 
                            #                                                         ).all()
                            #                 results_device_group_dict = [row._asdict() for row in result_device_group_rs485]  
                            #                 db.close()                                          
                            #                 # init restart pm2 app same rs485
                            #                 await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                            #                 # restart pm2 app log
                            #                 pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                            #                 await restart_program_pm2_many(pm2_app_list) 
                            #         elif result_find_app_pm2!=100:
                            #             print('---------- create group RS485 same com port when list device empty ----------')
                            #             # check group rs485 same com port
                            #             sql_query_select_device= cov_xml_sql("deviceConfig.xml","select_all_device",
                            #                                                     {"id_communication":id_communication})
                            #             result_device_group_rs485 =  db.execute(
                            #                                                     text(sql_query_select_device), 
                            #                                                         ).all()
                            #             results_device_group_dict = [row._asdict() for row in result_device_group_rs485] 
                            #             db.close()                                                       
                            #             # init restart pm2 app same rs485
                            #             await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                            #             # restart pm2 app log
                            #             pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
                            #             result=await restart_program_pm2_many(pm2_app_list)
                        case "UpdateDev":
                            pass
                        case "UpdateTemplate":
                            pass
                        case "DeleteTemplate":
                            pass
        except Exception as err:
            print(f"Error PM2: '{err}'")
    async def deviceListSub(self):
        try:
            db=get_db()
            result_project=db.query(deviceList_models.Device_list).all()
            db.close()
            # 
            Topic=self.MQTT_TOPIC+"/"+"Devices"
            client = mqttools.Client(host=self.MQTT_BROKER, 
                                port=self.MQTT_PORT ,
                                username= self.MQTT_USERNAME, 
                                password=bytes(self.MQTT_PASSWORD, 'utf-8'))
        
            await client.start()
            await client.subscribe(Topic+"/#")
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                print(f'Topic:   {message.topic}')
                result=json.loads(message.message.decode())
                
                for i,item in enumerate(self.DeviceList):
                    # print('------------------')
                    # print(item)
                    # print(f'{Topic}/{item["id_device"]}')
                    if message.topic==f'{Topic}/{item["id_device"]}':
                        # print(item)
                        self.DeviceList[i]["id_device_type"]=result["id_device_type"]
                        self.DeviceList[i]["name_device_type"]=result["name_device_type"]
                        self.DeviceList[i]["status_device"]=result["status_device"]
                        self.DeviceList[i]["timestamp"]=result["timestamp"]
                        self.DeviceList[i]["message"]=result["message"]
                        self.DeviceList[i]["status_register"]=result["status_register"]
                        self.DeviceList[i]["point_count"]=result["point_count"]
                        self.DeviceList[i]["parameters"]=result["parameters"]
                        self.DeviceList[i]["fields"]=result["fields"]
                        self.DeviceList[i]["mppt"]=result["mppt"]
                        
                        # for item in result["parameters"]:
                        #     print(len(item['fields']))
                        print(f'MQTT message size: {sys.getsizeof(self.DeviceList)} bytes')
                    
        except Exception as err:
            print('Error MQTT deviceListSub')
    async def deviceListPub(self):
        try:
                # [
                #     {   "id":296,
                #         "name":"ABB",
                #         "point_p":"",
                #         "model":"",
                #         "realtime":[]
                #     }
                # ]
                
            # topic=f"{self.MQTT_TOPIC_CLOUD}/Devices/All"
            # db=get_db()
            # result_project=db.query(deviceList_models.Device_list).filter_by(status=1).all()
            # db.close()
            # param=[]
            # for item in result_project:
            #     self.DeviceList.append({
            #         "id_device":item.id,
            #         "device_name":item.name,
            #     })
            
            # while True:
            #     param=self.DeviceList
            #     mqtt_public_common(self.MQTT_BROKER_CLOUD,
            #                     self.MQTT_PORT_CLOUD,
            #                     topic,
            #                     self.MQTT_USERNAME_CLOUD,
            #                     self.MQTT_PASSWORD_CLOUD,
            #                     param)
            #     await asyncio.sleep(2)
            topic=f"{self.MQTT_TOPIC}/Devices/All"
            db=get_db()
            result_project=db.query(deviceList_models.Device_list).filter_by(status=1).all()
            db.close()
            param=[]
            for item in result_project:
                self.DeviceList.append({
                    "id_device":item.id,
                    "device_name":item.name,
                    "mode":item.mode,
                    "parameters":[]
                })
            
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
                await asyncio.sleep(2)
        except Exception as err:
            print('Error MQTT deviceListPub')

async def main():
    tasks = []
    db=get_db()
    result_project=db.query(project_models.Project_setup).first()
    db.close()
    MQTT_TOPIC=result_project.serial_number
    
    MQTT_BROKER_CLOUD=result_project.mqtt_broker_cloud
    MQTT_PORT_CLOUD=result_project.mqtt_port_cloud
    MQTT_TOPIC_CLOUD=result_project.serial_number
    MQTT_USERNAME_CLOUD=result_project.mqtt_username_cloud
    MQTT_PASSWORD_CLOUD=result_project.mqtt_password_cloud
    print(f'MQTT_TOPIC: {MQTT_TOPIC}')
    api_gateway=apiGateway(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_TOPIC,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            MQTT_BROKER_CLOUD,
                            MQTT_PORT_CLOUD,
                            MQTT_TOPIC_CLOUD,
                            MQTT_USERNAME_CLOUD,
                            MQTT_PASSWORD_CLOUD,
                            )
    tasks.append(asyncio.create_task(
        api_gateway.managerApplicationsWithPM2()))
    tasks.append(asyncio.create_task(
        api_gateway.deviceListSub()))
    tasks.append(asyncio.create_task(
        api_gateway.deviceListPub()))
    
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('API GATEWAY stopped.')
        sys.exit(0)
