# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import json
import logging
import os
import secrets
import sys
import time
from datetime import datetime
from typing import Union

import mqttools
import mysql.connector
import paho.mqtt.publish as publish
from async_timeout import timeout
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
# 
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
from test.config import Config

from utils import path_directory_relative
from utils.libMySQL import *

# 
# DATABASE_HOSTNAME = Config.DATABASE_HOSTNAME
# DATABASE_PORT = Config.DATABASE_PORT
# DATABASE_PASSWORD = Config.DATABASE_PASSWORD
# DATABASE_NAME = Config.DATABASE_NAME
# DATABASE_USERNAME = Config.DATABASE_USERNAME
# 
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC 
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD


def connect(host, port,username, password, db):
    return mysql.connector.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=db,
       
    )

app = FastAPI(
     title="FastAPI",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url = None,
)
security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "123654789")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_swagger_documentation(username: str = Depends(get_current_username)):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")


@app.get("/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(get_current_username)):
    return get_redoc_html(openapi_url="/openapi.json", title="docs")


@app.get("/openapi.json", include_in_schema=False)
async def openapi(username: str = Depends(get_current_username)):
    return get_openapi(title=app.title, version=app.version, routes=app.routes)
class device_control(BaseModel):
    # {
    #     "DEVICE_ID":"",
    #     "DEVICE_NAME"
    #     "TAG_NAME":"",
    #     "VALUE":100
    # }
    # DEVICE_NAME: str | None = None
    DEVICE_ID: int
    DEVICE_NAME: str
    TAG_NAME: str
    VALUE: float
@app.post("/device_control")
async def write_device(control:device_control):
    try:
        
        # --------------------------------------------------
        topic_public="IPC|1|UNO-DM-3.3-TL-PLUS|control"
        mqtt_host=MQTT_BROKER 
        mqtt_port=MQTT_PORT
        mqtt_username=MQTT_USERNAME
        mqtt_password=MQTT_PASSWORD
        data_send=  {
                    "DEVICE_NAME":"UNO-DM-3.3-TL-PLUS",
                    "CODE":1 
                    }
        payload = json.dumps(data_send)
        publish.single(topic_public, payload, hostname=mqtt_host,
                        retain=False, port=mqtt_port,
                        auth = {'username':f'{mqtt_username}', 
                                'password':f'{mqtt_password}'})
        # --------------------------------------------------
        topic_subscribe="IPC|1|UNO-DM-3.3-TL-PLUS|feedback"

        async def feedback_device():
            
            client = mqttools.Client(host=mqtt_host, 
                                            port=mqtt_port,
                                            username= mqtt_username, 
                                            password=bytes(mqtt_password, 'utf-8'),
                                            session_expiry_interval=1,
                                            )
            await client.start()
            await client.subscribe(topic_subscribe)

            while True:
                
                # await asyncio.sleep(10)
                message = await client.messages.get()

                if message is None:
                    print('Broker connection lost!')
                print(f'Topic:   {message.topic}')
                result=json.loads(message.message.decode())
                print(f'Message: {result}')
                data="111"
                if message.topic:
                    return data
                
                                    
            
        async with timeout(5) as cm:
            response=  await feedback_device() 
            return {"item_id": response} 
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
    # time.sleep(2)
    