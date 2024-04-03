# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import json
import logging
import os
import subprocess
import sys
from pathlib import Path

import mybatis_mapper2sql
import paho.mqtt.publish as publish
from passlib.context import CryptContext
# from database import get_db
# from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
#                      Response, status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.project.models as project_models
import api.domain.template.models as template_models
import model.models as models
from configs.config import Config
from database.db import get_db

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC 
# IPC/Init/API/Requests
# IPC/Init/API/Responses
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
# Describe functions before writing code
# /**
# 	 * @description public data MQTT
# 	 * @author vnguyen
# 	 * @since 25-03-2024
# 	 * @param {data_send}
# 	 * @return data ()
# 	 */
def mqtt_public(Topic,data_send):
    try:
        db=get_db()
        result_project=db.query(project_models.Project_setup).first()
        db.close()
        # 
        host=MQTT_BROKER
        port=MQTT_PORT
        username=MQTT_USERNAME
        password=MQTT_PASSWORD
        # 
        MQTT_TOPIC=result_project.serial_number+Topic
        payload = json.dumps(data_send)
        publish.single(MQTT_TOPIC, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")
# Describe functions before writing code
# /**
# 	 * @description public data MQTT
# 	 * @author vnguyen
# 	 * @since 02-04-2024
# 	 * @param {data_send}
# 	 * @return data ()
# 	 */
def mqtt_public_common(host,port,topic,username,password,data_send):
    try:
        # 
        
        # print(host)
        # print(port)
        # print(topic)
        # print(username)
        # print(password)
        
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")