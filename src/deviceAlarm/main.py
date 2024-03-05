# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import json
import os
import sys
import time
from datetime import datetime as DT
from datetime import timedelta
from time import sleep

import mqttools
import paho.mqtt.publish as publish
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from colorama import Back, Fore, Style, init
from dateutil import parser
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, aliased
from termcolor import colored

# Color print
init()
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
# 
import api.domain.alarms.models as alarms_models
import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.project.models as project_models
import api.domain.template.models as template_models
import model.models as models
# 
from configs.config import Config
from database.db import get_db

# local_session=Session(bind=engine)

# Subscribe -> IPC/Alarm/Group/1 ... n
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC +"/Alarm/Group/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
TIME_TOLERANCE=10
# For example
json_alert={
    "id_device":1,
    "error_code":"100"
}
# 
db=get_db()

class AlarmLog:
    history_data={}
    def __init__(self,MQTT_BROKER="127.0.0.1",
                    MQTT_PORT=1883,
                    MQTT_TOPIC="",
                    MQTT_USERNAME="",
                    MQTT_PASSWORD="",
                    TABLE_CODE_ERROR=[],
                    TIME_TOLERANCE=10
                    ):

        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOPIC = MQTT_TOPIC
        self.MQTT_USERNAME = MQTT_USERNAME
        self.MQTT_PASSWORD = MQTT_PASSWORD
        self.TABLE_CODE_ERROR=TABLE_CODE_ERROR
        self.TIME_TOLERANCE=TIME_TOLERANCE
    # Describe functions before writing code
    # /**
    # 	 * @description insert log alert
    # 	 * @author vnguyen
    # 	 * @since 19-01-2024
    # 	 * @param {ID_DEVICE_GROUP,ID_DEVICE,ERROR_CODE}
    # 	 * @return data ()
    # 	 */
    def insert_log_alert(self,ID_DEVICE_GROUP: int,ID_DEVICE: int,ERROR_CODE: str):

        error_list=[item.__dict__ for item in self.TABLE_CODE_ERROR if 
                    item.id_device_group== int(ID_DEVICE_GROUP) and 
                    item.error_code ==str(ERROR_CODE) ]
        if error_list:
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                id=now.strftime("%Y%m%d%H%M%S")+str(int(now.microsecond/10)).zfill(5)
                new_alarm=alarms_models.Alarm(id=int(id),id_device=ID_DEVICE,id_error=error_list[0]["id"])
                db.add(new_alarm)
                db.commit()
            except Exception as err:
                db.rollback()
                print(err)
    # Describe functions before writing code
    # /**
    # 	 * @description insert log alert
    # 	 * @author vnguyen
    # 	 * @since 19-01-2024
    # 	 * @param {ID_DEVICE_GROUP}
    # 	 * @return data ()
    # 	 */
    async def mqtt_subs_alarm(self,ID_DEVICE_GROUP):
        try:

            MQTT_TOPIC =self.MQTT_TOPIC+ID_DEVICE_GROUP
            print(f'MQTT_TOPIC|{ID_DEVICE_GROUP}: {MQTT_TOPIC}')
            client = mqttools.Client(host=self.MQTT_BROKER, 
                                    port=self.MQTT_PORT,
                                    username= self.MQTT_USERNAME, 
                                    password=bytes(self.MQTT_PASSWORD, 'utf-8'))
            await client.start()
            await client.subscribe(MQTT_TOPIC)
            
            while True:
                message = await client.messages.get()
                if message is None:
                    print('Broker connection lost!')
                    break
                print(f'-------------------------------------------')
                print(f'Topic:   {message.topic}')
                result=json.loads(message.message.decode())
                print(f'Message: {result}')

                if "id_device" in result.keys() and "error_code" in result.keys():
                    id_device=result['id_device']
                    error_code=result['error_code']
                    print(f'ID_DEVICE_GROUP:   {ID_DEVICE_GROUP}')
                    print(f'error_code:   {error_code}')
                    # ------------------------------------
                    error_setup=[item.__dict__ for item in self.TABLE_CODE_ERROR if item.id_device_group== int(ID_DEVICE_GROUP) and 
                                                                                    item.error_code == str(error_code) ]
                    error_exist=0

                    if error_setup:
                        time_limit_lo=error_setup[0]["time_limit_alarm"]
                        time_limit_hi=error_setup[0]["time_limit_alarm"]+self.TIME_TOLERANCE
                        number_limit=error_setup[0]["number_limit_alarm"]
                    
                        # ------------------------------------
                        event=f'dev{id_device}_{error_code}'
                        dt = datetime.datetime.now(
                        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                        if event in self.history_data.keys():
                            count=self.history_data[event]["count"]+1
                            print('------------------------------------')
                            print(f'count error: {count}')
                            timestamp_last=self.history_data[event]["date_time"]
                            time1 = parser.parse(timestamp_last)
                            time2 = parser.parse(dt)
                            time_distance=round(((time2-time1) / timedelta(seconds=1)),2)
                            print(f'time_limit_Lo: {time_limit_lo} |time_limit_Hi: {time_limit_hi} | time_distance: {time_distance}')
                            if time_distance>=time_limit_lo and time_distance<=time_limit_hi:
                                #  check repeat event
                                if number_limit==1:
                                    self.history_data={**self.history_data,
                                                event:{
                                                "error_code":error_code,
                                                "date_time":dt,
                                                "count":0
                                    }}

                                    print(colored("Alert 1 -------------------------------", 'green'))
                                    error_exist=1
                                else:
                                    if count >=number_limit:
                                        self.history_data.update({
                                            event:{
                                                "error_code":error_code,
                                                "date_time":dt,
                                                "count":0
                                        }
                                        })
                                        # log to DB
                                        print(colored("Alert 2 -------------------------------", 'green'))
                                        error_exist=2
                                    # If number repeat < set point
                                    else:
                                        self.history_data.update({
                                            event:{
                                                "error_code":error_code,
                                                "date_time":dt,
                                                "count":count
                                        }
                                        })
                            # If distance time > set point
                            elif time_distance>time_limit_hi:
                                self.history_data.update({
                                        event:{
                                        "error_code":error_code,
                                        "date_time":dt,
                                        "count":1
                                    }
                                    })
                                if number_limit==1:
                                    self.history_data.update({
                                        event:{
                                        "error_code":error_code,
                                        "date_time":dt,
                                        "count":0
                                    }
                                    })
                                    print(colored("Alert 3 -------------------------------", 'green'))
                                    error_exist=3
                        
                        else:
                            print(f'time_limit_Lo: {time_limit_lo} |time_limit_Hi: {time_limit_hi}')
                            print(f'number_limit_alarm: {number_limit}')
                            if number_limit==1:
                                self.history_data={**self.history_data,
                                            event:{
                                            "error_code":error_code,
                                            "date_time":dt,
                                            "count":0
                                }}
                                print(colored("Alert 4 -------------------------------", 'green'))
                                error_exist=4
                                
                            else:
                                self.history_data={**self.history_data,
                                        event:{
                                        "error_code":error_code,
                                        "date_time":dt,
                                        "count":1
                            }}
                    else:
                        print(colored("Error code not exist -------------------------------", 'red'))
                    if error_exist>0:
                        print(colored(f'had error: {error_exist} -------------------------------', 'yellow'))
                        
                        self.insert_log_alert(ID_DEVICE_GROUP,id_device,error_code)
                        error_exist=0
                        
                print(f'history_data: {self.history_data}')
        except Exception as err:
            print(f"Error MQTT subscribe: '{err}'")
async def main():
    tasks = []
    
    device_query=db.query(deviceList_models.Device_list).filter_by(status=1).all()
    project_setup_query=db.query(project_models.Project_setup).filter(project_models.Project_setup.id==1).first()
    
    if project_setup_query and device_query:
        group_list= list(set([item.id_device_group for item in device_query]))
        ERROR_QUERY=db.query(alarms_models.Error).filter(alarms_models.Error.status==1).all()
        mqtt_alert=AlarmLog(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_TOPIC,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            ERROR_QUERY,
                            TIME_TOLERANCE
                            )
        for item in group_list:
            tasks.append(asyncio.create_task(mqtt_alert.mqtt_subs_alarm(str(item))))
    await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())