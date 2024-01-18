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
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from termcolor import colored

# Color print
init()

def path_directory_relative(project_name):
    if project_name =="":
        return -1
    path_os=os.path.dirname(__file__)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
        return -1
    result=path_os[0:int(index_os)+len(string_find)]
    return result
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)
from config import Config

# Subscribe -> IPC/Alarm/Group/1 ... n
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC +"/Alarm/Group/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
# For example
json_alert={
    "id_device":1,
    "error_code":"100"
}
# 
from models import (Alarm, Device_list, Error, Project_setup, Screen, Session,
                    engine)

local_session=Session(bind=engine)
class AlarmLog:
    history_data={}
    def __init__(self,MQTT_BROKER="127.0.0.1",
                    MQTT_PORT=1883,
                    MQTT_TOPIC="",
                    MQTT_USERNAME="",
                    MQTT_PASSWORD="",
                    TABLE_CODE_ERROR=[],
                    NUMBER_LIMIT_ALARM=1,
                    TIME_LIMIT_ALARM=5
                    ):

        self.MQTT_BROKER = MQTT_BROKER
        self.MQTT_PORT = MQTT_PORT
        self.MQTT_TOPIC = MQTT_TOPIC
        self.MQTT_USERNAME = MQTT_USERNAME
        self.MQTT_PASSWORD = MQTT_PASSWORD
        self.TABLE_CODE_ERROR=TABLE_CODE_ERROR
        self.NUMBER_LIMIT_ALARM=NUMBER_LIMIT_ALARM
        self.TIME_LIMIT_ALARM=TIME_LIMIT_ALARM
    def log_alert(self,id_device,error_code):
        error_list=[item.__dict__ for item in self.TABLE_CODE_ERROR if item.id_device_group==1 and item.error_code ==error_code ]
        if error_list:
            try:
                now = datetime.datetime.now(datetime.timezone.utc)
                id=now.strftime("%Y%m%d%H%M%S")+str(int(now.microsecond/10)).zfill(5)
                new_alarm=Alarm(id=int(id),id_device=id_device,id_error=error_list[0]["id"])
                local_session.add(new_alarm)
                local_session.commit()
            except Exception as err:
                local_session.rollback()
                print(err)
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
                    pass
                    id_device=result['id_device']
                    error_code=result['error_code']
                    
                    event=f'dev{id_device}_{error_code}'
                    dt = datetime.datetime.now(
                    datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    time_limit=self.TIME_LIMIT_ALARM+10
                    if event in self.history_data.keys():
                        count=self.history_data[event]["count"]+1
                        print('------------------------------------')
                        print(f'count: {count}')
                        timestamp=self.history_data[event]["date_time"]
                        time1 = parser.parse(timestamp)
                        time2 = parser.parse(dt)
                        dt_repeat=round(((time2-time1) / timedelta(seconds=1)),2)
                        
                        
                        print(f'time_limit_Lo: {self.TIME_LIMIT_ALARM} |time_limit_Hi: {time_limit} | dtime_repeat: {dt_repeat}')
                        if dt_repeat>=self.TIME_LIMIT_ALARM and dt_repeat<=time_limit:
                            #  check repeat event
                            if self.NUMBER_LIMIT_ALARM==1:
                                self.history_data={**self.history_data,
                                            event:{
                                            "error_code":error_code,
                                            "date_time":dt,
                                            "count":0
                                }}

                                print(colored("Alert 1 -------------------------------", 'red'))
                            else:
                                if count >=self.NUMBER_LIMIT_ALARM:
                                    self.history_data.update({
                                        event:{
                                            "error_code":error_code,
                                            "date_time":dt,
                                            "count":0
                                    }
                                    })
                                    # log to DB
                                    print(colored("Alert 2 -------------------------------", 'red'))
                                # If number repeat < set point
                                else:
                                    self.history_data.update({
                                        event:{
                                            "error_code":error_code,
                                            "date_time":dt,
                                            "count":count
                                    }
                                    })
                        # If time repeat > setpoint
                        elif dt_repeat>time_limit:
                            self.history_data.update({
                                    event:{
                                    "error_code":error_code,
                                    "date_time":dt,
                                    "count":1
                                }
                                })
                            if self.NUMBER_LIMIT_ALARM==1:
                                self.history_data.update({
                                    event:{
                                    "error_code":error_code,
                                    "date_time":dt,
                                    "count":0
                                }
                                })
                                print(colored("Alert 3 -------------------------------", 'red'))
                    
                    else:
                        print('===========================')
                        print(f'time_limit_Lo: {self.TIME_LIMIT_ALARM} |time_limit_Hi: {time_limit}')
                        print(f'NUMBER_LIMIT_ALARM: {self.NUMBER_LIMIT_ALARM}')
                        if self.NUMBER_LIMIT_ALARM==1:
                            self.history_data={**self.history_data,
                                        event:{
                                        "error_code":error_code,
                                        "date_time":dt,
                                        "count":0
                            }}
                            print(colored("Alert 4 -------------------------------", 'red'))
                            self.log_alert(id_device,error_code)
                        else:
                            self.history_data={**self.history_data,
                                    event:{
                                    "error_code":error_code,
                                    "date_time":dt,
                                    "count":1
                        }}
                print(f'history_data: {self.history_data}')
        except Exception as err:
            print(f"Error MQTT subscribe: '{err}'")
async def main():
    tasks = []
    
    
    device_query=local_session.query(Device_list).filter(Device_list.status==1).all()
    project_setup_query=local_session.query(Project_setup).filter(Project_setup.id==1).first()
    
    
    if project_setup_query and device_query:
        group_list= list(set([item.id_device_group for item in device_query]))
        NUMBER_LIMIT_ALARM=project_setup_query.number_limit_alarm
        TIME_LIMIT_ALARM=project_setup_query.time_limit_alarm
        ERROR_QUERY=local_session.query(Error).filter(Error.status==1).all()
        
        mqtt_alert=AlarmLog(MQTT_BROKER,
                            MQTT_PORT,
                            MQTT_TOPIC,
                            MQTT_USERNAME,
                            MQTT_PASSWORD,
                            ERROR_QUERY,
                            NUMBER_LIMIT_ALARM,
                            TIME_LIMIT_ALARM
                            )
        for item in group_list:
            tasks.append(asyncio.create_task(mqtt_alert.mqtt_subs_alarm(str(item))))
    await asyncio.gather(*tasks, return_exceptions=False)

if __name__ == "__main__":
    asyncio.run(main())