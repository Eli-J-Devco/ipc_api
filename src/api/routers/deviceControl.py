# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
import os
import sys
import asyncio
# import mqtt
from pathlib import Path
import paho.mqtt.publish as publish
import mqttools
# import oauth2
import psutil
# import schemas
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                    status)
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
# from test.config import Config

# import library 
from utils.libMQTT import *
from utils.libTime import *
from utils.libMySQL import *
from utils.libModBus import *
from configs.config import *
from database.db import get_db
from async_timeout import timeout

import secrets


sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
import api.domain.deviceControl.models as deviceControl_models
import api.domain.deviceControl.schemas as deviceControl_schemas
import model.models as models
import model.schemas as schemas
import utils.oauth2 as oauth2

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
router = APIRouter(
    prefix="/deviceControl",
    tags=['deviceControl']
)
# Describe functions before writing code
# /**
# 	 * @description get_mybatis
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {file_name}
# 	 * @return data (query)
# 	 */
def get_mybatis(file_name):
    try:
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+file_name)
        statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
        result={}
        for item,value in enumerate(statement):
            for key in value.keys():
                result[key]=value[key]   

        return result  
    except Exception as e:
        print('An exception occurred:',e)
        return -1 
    
# Describe functions before writing code
# /**
# 	 * @description get ethernet
# 	 * @author vnguyen
# 	 * @since 11-03-2024
# 	 * @param {id,db}
# 	 * @return data (device_control)
# 	 */  
@router.post('/on_off_inv/{id_device}', )
# def device_control(id_device : int ,bitcontrol : bool,db: Session = Depends(get_db), 
#                 current_user: int = Depends(oauth2.get_current_user) ):
async def device_control(id_device : int , bitcontrol : bool ):
    
    # query sql 
    global QUERY_INFORMATION_CONNECT_MODBUSTCP
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    
    
    # get time UTC
    current_time = get_utc()
    start_time = time.time()
    
    # Convert id (int) => string
    sql_id_str = ""
    sql_id_str = str(id_device)
    
    # information MQTT 
    topicPublic= "G83VZT33" + "/Control/" + sql_id_str +  "/" + "Write" 
    topicSud= "G83VZT33" + "/Control/" + sql_id_str +  "/" + "Feedback" 
    mqtt_host=MQTT_BROKER 
    mqtt_port=MQTT_PORT
    mqtt_username=MQTT_USERNAME
    mqtt_password=MQTT_PASSWORD
    comment = ""
    
    # result Modbus
    results_device_type = []
    results_register = []
    results_device_modbus = []
    
    # information Modbus 
    required_pointkeys = ['ControlINV']
    filtered_results_register = []
    parametter = []
    
    # information Modbus 
    register = ""
    device_name = ""
    status_device = ""
    id_device_return = ""
    mode = ""
    token = ""
    
    result_mybatis = get_mybatis('/mybatis/control.xml')
    try:
        QUERY_INFORMATION_CONNECT_MODBUSTCP = result_mybatis["QUERY_INFORMATION_CONNECT_MODBUSTCP"]
        QUERY_TYPE_DEVICE = result_mybatis["QUERY_TYPE_DEVICE"]
        QUERY_REGISTER_DATATYPE = result_mybatis["QUERY_REGISTER_DATATYPE"]

    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_TYPE_DEVICE or not QUERY_REGISTER_DATATYPE or not QUERY_INFORMATION_CONNECT_MODBUSTCP:
        print("Error not found data in file mybatis") 
        return -1
    
    # check device is not INV 
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        print("No devices selected")
        comment = "No devices selected"
    
    # if device is INV 
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            
            if results_device_modbus :
                device_name = results_device_modbus[0]['name']
            else :
                pass
            
            # Create a new list to store elements that satisfy the condition
            if results_register :
                filtered_results_register = [item for item in results_register if item['id_pointkey'] in required_pointkeys]
                parametter = [{'id_pointkey': item['id_pointkey']} for item in filtered_results_register]

                # Iterate through the new list to assign values from the corresponding variables
                for item in parametter:
                    if item['id_pointkey'] == 'ControlINV':
                        item['value'] = bitcontrol
                    
                    comment = "pushlid successfully to MQTT" 
            else:
                print("No data found in results_register")
                comment = "No data found in results_register"
        else:
            print("device can not control")
            comment = "device can not control"
    else :
        comment = print("device does not exist")
        comment = "device does not exist"
        
    try:
        data_send = {
            "id_device":sql_id_str,
            "parameter" : parametter,
            }
        
        push_data_to_mqtt(mqtt_host,
                mqtt_port,
                topicPublic,
                mqtt_username,
                mqtt_password,
                data_send)
        
        client = mqttools.Client(host=mqtt_host, port=mqtt_port, username=mqtt_username, password=bytes(mqtt_password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topicSud)
        
        while True:
            try:
                message = await client.messages.get()
            except asyncio.TimeoutError:
                if time.time() - start_time > 15:
                    print("MQTT connection timed out")
                    return JSONResponse(status_code=500, content={"error": "MQTT Connection Timeout"})
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            mqtt_result = json.loads(message.message.decode())
            
            # if mqtt_result and all(key in mqtt_result for key in ['id_device', 'device_name', 'status' ,'token' ]):
            if mqtt_result and all(key in mqtt_result for key in ['id_device', 'device_name', 'status' ]):
                device_name = mqtt_result['device_name']
                status_device = mqtt_result['status']
                id_device_return = mqtt_result['id_device']
                # token = mqtt_result['token']
                
                return {
                    'id_device_return': id_device_return,
                    'device_name': device_name,
                    'status_device': status_device,
                    # 'token': token,
                }

                
    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

# Describe functions before writing code
# /**
# 	 * @description get ethernet
# 	 * @author vnguyen
# 	 * @since 11-03-2024
# 	 * @param {id,db}
# 	 * @return data (device_control)
# 	 */  
@router.post('/setup_control /{id_device}', )
# def device_control(id_device : int ,bitcontrol : bool,db: Session = Depends(get_db), 
#                 current_user: int = Depends(oauth2.get_current_user) ):
async def setup_control(id_device : int , WMax : int , WMaxPercent : int ,WMaxPercentEnable : bool 
                        ,PFSet : int ,PFSetEnable : bool ,VarMaxPercent : int ,VarMaxPercentEnable : bool ):
    
    # query sql 
    global QUERY_INFORMATION_CONNECT_MODBUSTCP
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    
    
    # get time UTC
    start_time = time.time()
    
    # Convert id (int) => string
    sql_id_str = ""
    sql_id_str = str(id_device)
    
    # information MQTT 
    topicPublic= "G83VZT33" + "/Control/" + sql_id_str +  "/" + "Write" 
    topicSud= "G83VZT33" + "/Control/" + sql_id_str +  "/" + "Feedback" 
    mqtt_host=MQTT_BROKER 
    mqtt_port=MQTT_PORT
    mqtt_username=MQTT_USERNAME
    mqtt_password=MQTT_PASSWORD
    comment = ""
    
    # result Modbus
    results_device_type = []
    results_register = []
    results_device_modbus = []
    
    
    # information Modbus 
    required_pointkeys = ['WMax', 'WMaxPercent', 'WMaxPercentEnable', 'PFSet', 'PFSetEnable', 'VarMaxPercent', 'VarMaxPercentEnable']
    filtered_results_register = []
    parametter = []
    
    device_name = ""
    status_write_inv = ""
    id_device_return = ""
    token = ""
    
    result_mybatis = get_mybatis('/mybatis/control.xml')
    try:
        QUERY_INFORMATION_CONNECT_MODBUSTCP = result_mybatis["QUERY_INFORMATION_CONNECT_MODBUSTCP"]
        QUERY_TYPE_DEVICE = result_mybatis["QUERY_TYPE_DEVICE"]
        QUERY_REGISTER_DATATYPE = result_mybatis["QUERY_REGISTER_DATATYPE"]

    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_TYPE_DEVICE or not QUERY_REGISTER_DATATYPE or not QUERY_INFORMATION_CONNECT_MODBUSTCP:
        print("Error not found data in file mybatis") 
        return -1
    
    # check device is not INV 
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        print("No devices selected")
        comment = "No devices selected"
    
    # if device is INV 
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            
            if results_device_modbus :
                device_name = results_device_modbus[0]['name']
            else :
                pass
            
            # Create a new list to store elements that satisfy the condition
            if results_register :
                filtered_results_register = [item for item in results_register if item['id_pointkey'] in required_pointkeys]
                parametter = [{'id_pointkey': item['id_pointkey']} for item in filtered_results_register]
                # Iterate through the new list to assign values from the corresponding variables
                for item in parametter:
                    if item['id_pointkey'] == 'WMax':
                        item['value'] = WMax
                    elif item['id_pointkey'] == 'WMaxPercent':
                        item['value'] = WMaxPercent
                    elif item['id_pointkey'] == 'WMaxPercentEnable':
                        item['value'] = WMaxPercentEnable
                    elif item['id_pointkey'] == 'PFSet':
                        item['value'] = PFSet
                    elif item['id_pointkey'] == 'PFSetEnable':
                        item['value'] = PFSetEnable
                    elif item['id_pointkey'] == 'VarMaxPercent':
                        item['value'] = VarMaxPercent
                    elif item['id_pointkey'] == 'VarMaxPercentEnable':
                        item['value'] = VarMaxPercentEnable
                    
                    comment = "pushlid successfully to MQTT"

            else:
                print("No data found in results_register")
                comment = "No data found in results_register"
        else:
            print("device can not control")
            comment = "device can not control"
    else :
        comment = print("device does not exist")
        comment = "device does not exist"
    try:
        data_send = {
            "id_device":sql_id_str,
            "parametter" : parametter,
            }
        push_data_to_mqtt(mqtt_host,
                mqtt_port,
                topicPublic,
                mqtt_username,
                mqtt_password,
                data_send)
        
        client = mqttools.Client(host=mqtt_host, port=mqtt_port, username=mqtt_username, password=bytes(mqtt_password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topicSud)
        
        while True:
            try:
                message = await client.messages.get()
            except asyncio.TimeoutError:
                if time.time() - start_time > 10:
                    print("MQTT connection timed out")
                    return JSONResponse(status_code=500, content={"error": "MQTT Connection Timeout"})
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            mqtt_result = json.loads(message.message.decode())
            
            if mqtt_result and all(key in mqtt_result for key in ['id_device', 'device_name', 'status']):
                device_name = mqtt_result['device_name']
                status_write_inv = mqtt_result['status']
                id_device_return = mqtt_result['id_device']
                
                return {
                    'id_device_return': id_device_return,
                    'device_name': device_name,
                    'status_device': status_write_inv,
                }

                
    except Exception as e:
        print(f"An error occurred: {e}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
            



        

    
