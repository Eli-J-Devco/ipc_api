import logging
import os
import sys
import asyncio
import datetime
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor

import mqttools
import mybatis_mapper2sql
import paho.mqtt.publish as publish
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
print(path)
from configs.config import Config
from utils.libMySQL import *
from database.db import get_db
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from sqlalchemy.orm import Session
from typing import Union
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
import utils.oauth2 as oauth2

app = FastAPI()

# Information MQTT
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC_PUB = Config.MQTT_TOPIC + "/Control" 
MQTT_USERNAME = Config.MQTT_USERNAME 
MQTT_PASSWORD = Config.MQTT_PASSWORD

bit_return = ""
id_device = ""

QUERY_INFORMATION_CONNECT_MODBUSTCP = ""
QUERY_ALL_DEVICES = ""
QUERY_TYPE_DEVICE = ""
QUERY_REGISTER_DATATYPE = ""
QUERY_DATATYPE = ""

from utils.logger_manager import LoggerSetup

# setup root logger
# logger_setup = LoggerSetup(path,"ControlDevice")
# LOGGER = logging.getLogger(__name__)
"""
project_setup ->    mode_control 0=Man 1=Zero Export 2= Limit P,Q
Mode = Man -> value direct to function read device
Mode = Zero Export ->   
Mode = Limit -> 
"""
class ControlRequest(BaseModel):
    bit_control: int
    p_out :int
    p_out : int
    s_out :int
    cosphi : int
#----------------------------------------
# /**
# 	 * @description take time 
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {}
# 	 * @return datetime
# 	 */
def get_utc():
    now=None
    try:
        now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        if now:
            return now
    except Exception as err:
        return None
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
# 	 * @description Modbus Function Codes
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {client, FUNCTION, ADDRs, COUNT, slave_ID}
# 	 * @return data (registers)
# 	 */
def select_function(client, FUNCTION, ADDRs, COUNT, slave_ID):
    try:
        match FUNCTION:
            case 0:# not used           
                return []
            case 1:# Read Coils
                ADDR = ADDRs                        
                result_rb = client.read_coils(
                                ADDR, COUNT, unit=slave_ID)
                return result_rb

            case 2:# Read Discrete Inputs      
                ADDR = ADDRs
                result_rb = client.read_discrete_inputs(
                                    ADDR, COUNT, unit=slave_ID)
                return result_rb
            
            case 3:# Read Holding Registers
                ADDR = ADDRs
                result_rb = client.read_holding_registers(
                                    ADDR, COUNT, unit=slave_ID)
                return result_rb

            case 4:# Read Input Registers
                ADDR = ADDRs
                result_rb = client.read_input_registers(
                                    ADDR, COUNT, unit=slave_ID)
                return result_rb
            case _:
                return []
    except Exception as err:
        print(f'Error select_function {err}')
        return []
# Describe funtion wwrite in device modbus TCP 
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
def write_modbus_tcp(client, unit, datatype,register, value):
    try:
        builder = BinaryPayloadBuilder(
        byteorder=Endian.Big)
        match datatype:
            case 3: # Short Signed 16-bit
                builder.add_16bit_int(int(value))
            case 4: # Word Unsigned 16-bit
                builder.add_16bit_uint(int(value))
            case 5: # Long Signed 32-bit
                builder.add_32bit_int(int(value))
            case 6: # DWord Unsigned 32-bit
                builder.add_32bit_uint(int(value))
            case 7: # LLong Signed 64-bit
                builder.add_64bit_int(int(value))
            case 8: # QWord Unsigned 64-bit
                builder.add_64bit_uint(int(value))
            case 9: # Float 32-bit real value IEEE-754
                builder.add_32bit_float(float(value))
            case 10: # Double 64-bit real value
                builder.add_64bit_float(float(value))
            case _:
                pass
        payload = builder.build()
        address=register
        result = client.write_registers(
        address, payload, skip_encode=True, unit=unit)
        print(f'result: {result.function_code }')
        if result.function_code == 16:
            msg ={ "msg":"Write success to INV-"+str(register),
                "code":result.function_code,
                "value":0
                }
        else:
            msg ={ "msg":"Write error to INV-"+str(register),
                "code":result.function_code,
                "value":1
                }
        return msg
    except Exception as err:
        print(f'Error write_modbus_tcp : {err}')
        return {
                "msg":err,
                "code":"",
                "value":2
            }
# ----- MQTT -----
# /**
# 	 * @description public data MQTT
# 	 * @author bnguyen
# 	 * @since 13-12-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
def push_data_to_mqtt(host, port,topic, username, password, data_send):
    try:
        payload = json.dumps(data_send)
        publish.single(topic, payload, hostname=host,
                    retain=False, port=port,
                    auth = {'username':f'{username}', 
                            'password':f'{password}'})
        # publish.single(Topic, payload, hostname=Broker,
        #             retain=False, port=Port)
    # except Error as err:
    #     print(f"Error MQTT public: '{err}'")
    except Exception as err:
    # except:
        
        print(f"Error MQTT public: '{err}'")
        pass
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(sql_id,host, port,topic, username, password):
    
    global QUERY_ALL_DEVICES
    global bit_control
    global bit_return
    
    current_time = get_utc()
    result_all = []
    sql_id_str = ""
    device_name = ""
    
    result_all = await MySQL_Select_v1(QUERY_ALL_DEVICES) 

    try:
        data_mqtt={
            "ID_DEVICE":sql_id,
            "STATUS_DEVICE":"ONLINE",
            "TIME_STAMP" :current_time,
            "STATUS_CONTROL_REQUEST": bit_control ,
            "STATUS_CONTROL_RETURN":bit_return,
            }
        
        # File creation time 
        sql_id_str = str(sql_id)
        device_name = [item['name'] for item in result_all if item['id'] == sql_id][0] 
        
        push_data_to_mqtt(host,
                port,
                topic + f"/"+sql_id_str+"|"+device_name,
                username,
                password,
                data_mqtt)
    except Exception as err:
        print('Error monitoring_device : ',err)
        
# Describe functions before writing code
# /**
# 	 * @description Control INV 
# 	 * @author bnguyen
# 	 * @since 19/3/2024
# 	 * @param {id_device}
# 	 * @return status device 
# 	 */
@app.post("/man_INV/{id_device}")
# async def control_man(request: Request, control_request: ControlRequest ,current_user: int = Depends(oauth2.get_current_user)):
async def control_man(request: Request,id_device:int ,control_request: ControlRequest ):
    
    bit_control = control_request.bit_control
    global bit_return

    global QUERY_INFORMATION_CONNECT_MODBUSTCP
    global QUERY_ALL_DEVICES
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    global QUERY_DATATYPE
    
    results_device_type = []
    results_device_modbus = []
    results_register = []
    results_datatype = []
    
    slave_ip =""
    slave_port = ""
    unit = ""
    type_datatype = ""
    datatype = ""
    register = ""
    max_watt = 0
    
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
    
    # truyeenf them so chay thiet bij vao
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        return print("No devices selected")
    
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
    
            if results_device_modbus :
                slave_ip = results_device_modbus[0]["tcp_gateway_ip"]
                slave_port = results_device_modbus[0]['tcp_gateway_port']
                unit = results_device_modbus[0]['rtu_bus_address']
                max_watt = results_device_modbus[0]['max_watt']
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
            
            results_datatype = MySQL_Select(QUERY_DATATYPE, (type_datatype,))
            if results_datatype :
                datatype = results_datatype[0]["value"]
            else :
                pass
            try:
                with ModbusTcpClient(slave_ip, port=slave_port, unit=unit, register=register, datatype=datatype ,value=max_watt) as client:
                    if bit_control == 1:
                        write_modbus_tcp(client, unit, datatype, register, value=max_watt)
                        bit_return = "INV Running"
                        
                    elif bit_control == 0:
                        write_modbus_tcp(client, unit, datatype, register, value=0)
                        bit_return = "INV Shutdown"
                        
            except ConnectionException as conn_err:
                print('Modbus Connection Error:', conn_err)
                return {"error": "Unable to connect to the device."}
            except ModbusException as modbus_err:
                print('Modbus Error:', modbus_err)
                return {"error": "Error communicating with the device."}
            except Exception as e:
                print(f"An error occurred: {e}")
                return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
            
            return {"message": "Control command sent successfully", "status_INV": bit_return}
        #-------------------------------------------------------
        else:
            return print("device can not control")
    else :
        return print("device does not exist")

@app.post("/input_P/{id_device}")
async def control_P(request: Request, control_request: ControlRequest ,current_user: int = Depends(oauth2.get_current_user)):
# async def control_man(request: Request,id_device:int ,control_request: ControlRequest ):
    
    p_out = control_request.p_out
    global bit_return

    global QUERY_INFORMATION_CONNECT_MODBUSTCP
    global QUERY_ALL_DEVICES
    global QUERY_TYPE_DEVICE
    global QUERY_REGISTER_DATATYPE
    global QUERY_DATATYPE
    
    
    results_device_type = []
    results_device_modbus = []
    results_register = []
    results_datatype = []
    
    slave_ip =""
    slave_port = ""
    unit = ""
    type_datatype = ""
    datatype = ""
    register = ""
    max_watt = 0
        
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
    
    # truyeenf them so chay thiet bij vao
    if id_device :
        results_device_type = MySQL_Select(QUERY_TYPE_DEVICE, (id_device,))
    else :
        return print("No devices selected")
    
    if results_device_type :
        if results_device_type[0]["name"] == "PV System Inverter" :
            results_device_modbus = MySQL_Select(QUERY_INFORMATION_CONNECT_MODBUSTCP, (id_device,))
            results_register = MySQL_Select(QUERY_REGISTER_DATATYPE, (id_device,))
    
            if results_device_modbus :
                slave_ip = results_device_modbus[0]["tcp_gateway_ip"]
                slave_port = results_device_modbus[0]['tcp_gateway_port']
                unit = results_device_modbus[0]['rtu_bus_address']
                max_watt = results_device_modbus[0]['max_watt']
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
            
            results_datatype = MySQL_Select(QUERY_DATATYPE, (type_datatype,))
            if results_datatype :
                datatype = results_datatype[0]["value"]
            else :
                pass
            try:
                with ModbusTcpClient(slave_ip, port=slave_port, unit=unit, register=register, datatype=datatype ,value=p_out) as client:
                        write_modbus_tcp(client, unit, datatype, register, value=p_out)
                        
            except ConnectionException as conn_err:
                print('Modbus Connection Error:', conn_err)
                return {"error": "Unable to connect to the device."}
            except ModbusException as modbus_err:
                print('Modbus Error:', modbus_err)
                return {"error": "Error communicating with the device."}
            except Exception as e:
                print(f"An error occurred: {e}")
                return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
            
            return {"message": "write the value down successfully ", "with capacity": p_out}
        #-------------------------------------------------------
        else:
            return print("device can not control")
    else :
        return print("device does not exist")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
# uvicorn src.deviceControl.main:app --reload
