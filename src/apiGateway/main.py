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
from utils.mqttManager import mqtt_public
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              find_program_pm2, restart_pm2_change_template,
                              restart_program_pm2, restart_program_pm2_many)

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC +"/Init"
# IPC/Init/API/Requests
# IPC/Init/API/Responses
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.template.models as template_models
import model.models as models


async def managerApplicationsWithPM2(host, port,topic, username, password):
    try:
        Topic=f'{topic}/API/Requests'
        client = mqttools.Client(host=host, 
                        port=port,
                        username= username, 
                        password=bytes(password, 'utf-8'))
        await client.start()
        await client.subscribe(Topic)
        while True:
            message = await client.messages.get()

            if message is None:
                print('Broker connection lost!')
                break
            print(f'Topic:   {message.topic}')
            result=json.loads(message.message.decode())
            print(f'Message: {result}')
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
                        pass
            
            
            
    except Exception as err:
        print(f"Error PM2: '{err}'")

async def main():
    tasks = []
    managerApplicationsWithPM2
    tasks.append(asyncio.create_task(
        managerApplicationsWithPM2(MQTT_BROKER,MQTT_PORT,
                                MQTT_TOPIC,MQTT_USERNAME,MQTT_PASSWORD)))
    
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(
            asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
        asyncio.run(main())
    except KeyboardInterrupt:
        print ('Port forwarding stopped.')
        sys.exit(0)
