# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
import os
import sys
from pathlib import Path

# import oauth2
import psutil
# import schemas
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# from test.config import Config

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
import utils.oauth2 as oauth2
from configs.config import *
from database.db import get_db

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORDS
router = APIRouter(
    prefix="/deviceControl",
    tags=['deviceControl']
)

# Describe functions before writing code
# /**
# 	 * @description get ethernet
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (EthernetOut)
# 	 */  
@router.post('/', )
def device_control( db: Session = Depends(get_db), 
                 current_user: int = Depends(oauth2.get_current_user) ):
    try:
        
        topicPublic="IPC/Control/Write/id of device/point"
        topicSubscribe="IPC/Control/Feedback/id of device/point"

        mqtt_host=MQTT_BROKER 
        mqtt_port=MQTT_PORT
        mqtt_username=MQTT_USERNAME
        mqtt_password=MQTT_PASSWORD
        data_send=  {
                    "DEVICE_NAME":"UNO-DM-3.3-TL-PLUS",
                    "CODE":1 
                    }
        return {
            "status_code":"ok"
        }
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")