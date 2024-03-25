# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import json
import os
import sys

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
    global QUERY_ALL_DEVICES
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    global QUERY_DATATYPE
    
    # get time UTC
    current_time = get_utc()
    
    # Convert id (int) => string
    sql_id_str = ""
    sql_id_str = str(id_device)
    
    # information MQTT 
    Token = secrets.token_urlsafe(16)
    topicPublic="IPC/Control/" + sql_id_str + "/" + "Status" + "/" + Token
    mqtt_host=MQTT_BROKER 
    mqtt_port=MQTT_PORT
    mqtt_username=MQTT_USERNAME
    mqtt_password=MQTT_PASSWORD
    
    # result Modbus
    results_device_type = []
    results_device_modbus = []
    results_register = []
    results_datatype = []
    results_write_modbus = []
    
    # information Modbus 
    device_name = ""
    slave_ip = ""
    slave_port = ""
    unit = ""
    type_datatype = ""
    datatype = ""
    register = ""
    status_device = ""
    code_value = 0 
    
    
    result_mybatis = get_mybatis('/mybatis/control.xml')
    try:
        QUERY_INFORMATION_CONNECT_MODBUSTCP = result_mybatis["QUERY_INFORMATION_CONNECT_MODBUSTCP"]
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TYPE_DEVICE = result_mybatis["QUERY_TYPE_DEVICE"]
        QUERY_REGISTER_DATATYPE = result_mybatis["QUERY_REGISTER_DATATYPE"]
        QUERY_DATATYPE = result_mybatis["QUERY_DATATYPE"]

    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_INFORMATION_CONNECT_MODBUSTCP or not QUERY_ALL_DEVICES or not QUERY_TYPE_DEVICE or not QUERY_REGISTER_DATATYPE or not QUERY_DATATYPE:
        print("Error not found data in file mybatis") 
        return -1
    
    # check device is not INV 
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        return print("No devices selected")
    
    # if device is INV 
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
    
            if results_device_modbus :
                slave_ip = results_device_modbus[0]["tcp_gateway_ip"]
                slave_port = results_device_modbus[0]['tcp_gateway_port']
                unit = results_device_modbus[0]['rtu_bus_address']
                max_watt = results_device_modbus[0]['max_watt']
                device_name = results_device_modbus[0]['name']
            else :
                pass
            if results_register:
                for item in results_register:
                    if item['id_pointkey'] == 'ControlINV':
                        register = item['register']
                        type_datatype = item['id_type_datatype']
                    else :
                        pass 
            else:
                print("No data found in results_register")
            
            # Find datatype register (int16,int32, float,...)
            results_datatype = MySQL_Select(QUERY_DATATYPE, (type_datatype,))
            if results_datatype :
                datatype = results_datatype[0]["value"]
            else :
                pass
            
            try:
                if slave_ip and slave_port and unit and register and datatype and bitcontrol :
                    with ModbusTcpClient(slave_ip, port=slave_port, unit=unit, register=register, datatype=datatype ,value=bitcontrol) as client:
                        if bitcontrol == True:
                            results_write_modbus = write_modbus_tcp(client, unit, datatype, register, value=bitcontrol)
                            
                        elif bitcontrol == False:
                            results_write_modbus = write_modbus_tcp(client, unit, datatype, register, value=bitcontrol)
                            
                    # get status INV 
                    code_value = results_write_modbus['code']
                    if code_value == 16 and bitcontrol == True:
                        status_device =" INV Running"
                    elif code_value == 16 and bitcontrol == False :
                        status_device =" INV ShutingDown"
                    if code_value == 144 :
                        status_device = "Write error to INV "
                else :
                    pass  
                
                data_send = {
                    "ID_DEVICE":sql_id_str,
                    "DEVICE_NAME":device_name,
                    "TIME_STAMP" :current_time,
                    "STATUS_CONTROL_REQUEST": bitcontrol ,
                    "FEEDBACK": results_write_modbus ,
                    "STATUS_DEVICE":status_device ,
                    "TOKEN":Token
                    }
                push_data_to_mqtt(mqtt_host,
                        mqtt_port,
                        topicPublic,
                        mqtt_username,
                        mqtt_password,
                        data_send)
                
                return {"Token": Token, "topicPublic": topicPublic, "reponseDevice": results_write_modbus}
                
            except ConnectionException as conn_err:
                print('Modbus Connection Error:', conn_err)
                return {"error": "Unable to connect to the device."}
            except ModbusException as modbus_err:
                print('Modbus Error:', modbus_err)
                return {"error": "Error communicating with the device."}
            except Exception as e:
                print(f"An error occurred: {e}")
                return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
            
        #-------------------------------------------------------
        else:
            return print("device can not control")
    else :
        return print("device does not exist")

# Describe functions before writing code
# /**
# 	 * @description get ethernet
# 	 * @author vnguyen
# 	 * @since 11-03-2024
# 	 * @param {id,db}
# 	 * @return data (device_control)
# 	 */  
@router.post('/p_out_inv/{id_device}', )
# def device_control(id_device : int ,bitcontrol : bool,db: Session = Depends(get_db), 
#                 current_user: int = Depends(oauth2.get_current_user) ):
async def device_control(id_device : int , p_out : int ):
    
    # query sql 
    global QUERY_INFORMATION_CONNECT_MODBUSTCP
    global QUERY_ALL_DEVICES
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    global QUERY_DATATYPE
    
    # get time UTC
    current_time = get_utc()
    
    # Convert id (int) => string
    sql_id_str = ""
    sql_id_str = str(id_device)
    
    # information MQTT 
    Token = secrets.token_urlsafe(16)
    topicPublic="IPC/Control/" + sql_id_str + "/" + "P" + "/" + Token
    mqtt_host=MQTT_BROKER 
    mqtt_port=MQTT_PORT
    mqtt_username=MQTT_USERNAME
    mqtt_password=MQTT_PASSWORD
    
    # result Modbus
    results_device_type = []
    results_device_modbus = []
    results_register = []
    results_datatype = []
    results_write_modbus = []
    
    # information Modbus 
    device_name = ""
    slave_ip = ""
    slave_port = ""
    unit = ""
    type_datatype = ""
    datatype = ""
    register = ""
    status_device = ""
    max_watt = 0
    code_value = 0 
    
    
    result_mybatis = get_mybatis('/mybatis/control.xml')
    try:
        QUERY_INFORMATION_CONNECT_MODBUSTCP = result_mybatis["QUERY_INFORMATION_CONNECT_MODBUSTCP"]
        QUERY_ALL_DEVICES = result_mybatis["QUERY_ALL_DEVICES"]
        QUERY_TYPE_DEVICE = result_mybatis["QUERY_TYPE_DEVICE"]
        QUERY_REGISTER_DATATYPE = result_mybatis["QUERY_REGISTER_DATATYPE"]
        QUERY_DATATYPE = result_mybatis["QUERY_DATATYPE"]

    except Exception as e:
            print('An exception occurred',e)
    
    if not QUERY_INFORMATION_CONNECT_MODBUSTCP or not QUERY_ALL_DEVICES or not QUERY_TYPE_DEVICE or not QUERY_REGISTER_DATATYPE or not QUERY_DATATYPE:
        print("Error not found data in file mybatis") 
        return -1
    
    # check device is not INV 
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        return print("No devices selected")
    
    # if device is INV 
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
    
            if results_device_modbus :
                slave_ip = results_device_modbus[0]["tcp_gateway_ip"]
                slave_port = results_device_modbus[0]['tcp_gateway_port']
                unit = results_device_modbus[0]['rtu_bus_address']
                device_name = results_device_modbus[0]['name']
            else :
                pass
            if results_register:
                for item in results_register:
                    if item['id_pointkey'] == 'WMax':
                        register = item['register']
                        type_datatype = item['id_type_datatype']
                    else :
                        pass 
            else:
                print("No data found in results_register")
            
            # Find datatype register (int16,int32, float,...)
            results_datatype = MySQL_Select(QUERY_DATATYPE, (type_datatype,))
            if results_datatype :
                datatype = results_datatype[0]["value"]
            else :
                pass
            
            
            try:
                with ModbusTcpClient(slave_ip, port=slave_port, unit=unit, register=register, datatype=datatype ,value=p_out) as client:
                        results_write_modbus = write_modbus_tcp(client, unit, datatype, register, value=p_out)
                # get status INV 
                code_value = results_write_modbus['code']
                if code_value == 16 :
                    status_device = "Check INV "
                if code_value == 144 :
                    status_device = "Write error to INV "
                    
                data_send = {
                    "ID_DEVICE":sql_id_str,
                    "DEVICE_NAME":device_name,
                    "TIME_STAMP" :current_time,
                    "POUT_REQUEST": p_out ,
                    "FEEDBACK": results_write_modbus ,
                    "STATUS_DEVICE":status_device ,
                    "TOKEN":Token
                    }
                push_data_to_mqtt(mqtt_host,
                        mqtt_port,
                        topicPublic ,
                        mqtt_username,
                        mqtt_password,
                        data_send)
                
                return {"Token": Token, "topicPublic": topicPublic, "reponseDevice": results_write_modbus}
                
            except ConnectionException as conn_err:
                print('Modbus Connection Error:', conn_err)
                return {"error": "Unable to connect to the device."}
            except ModbusException as modbus_err:
                print('Modbus Error:', modbus_err)
                return {"error": "Error communicating with the device."}
            except Exception as e:
                print(f"An error occurred: {e}")
                return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
            
        #-------------------------------------------------------
        else:
            return print("device can not control")
    else :
        return print("device does not exist")
        

    
