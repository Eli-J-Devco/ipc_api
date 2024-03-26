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
from configs.config import Config

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
        host=MQTT_BROKER
        port=MQTT_PORT
        username=MQTT_USERNAME
        password=MQTT_PASSWORD
        Topic=MQTT_TOPIC+Topic
        
        payload = json.dumps(data_send)
        publish.single(Topic, payload, hostname=host,
                       retain=False, port=port,
                       auth = {'username':f'{username}', 
                               'password':f'{password}'})
    except Exception as err:
        print(f"Error MQTT public: '{err}'")