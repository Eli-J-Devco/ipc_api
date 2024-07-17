# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import asyncio
import datetime
import json
# import math
import os
import sys

# import asyncio_mqtt as aiomqtt
# absDirname: D:\NEXTWAVE\project\ipc_api\driver_of_device
# absDirname=os.path.dirname(os.path.abspath(__file__))
import mqttools
# import mybatis_mapper2sql
# import paho.mqtt.publish as publish
import psutil
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

# import time
# from datetime import datetime as DT


sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
#                 ("src"))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from database.sql.device import all_query as device_query
from deviceDriver.monitoring import monitoring_service
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *
from utils.mqttManager import (gzip_decompress, mqtt_public,
                               mqtt_public_common, mqtt_public_paho,
                               mqtt_public_paho_zip, mqttService)

arr = sys.argv
print(f'arr: {arr}')
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC|device_id|device_name
# Subscribe -> IPC|device_id|device_name|control
MQTT_TOPIC = Config.MQTT_TOPIC +"/Dev/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD

MQTT_TOPIC_PUB_CONTROL = "/Control"
MQTT_TOPIC_PUD_MODE_DEVICE = "/Control/Setup/Mode/Write"
MQTT_TOPIC_SUD_MODE_SYSTEMP = "/Control/Setup/Mode/Feedback"
MQTT_TOPIC_SUD_CONTROL_MAN = "/Control/Write"
MQTT_TOPIC_SUD_CONTROL_AUTO = "/Control/WriteAuto"
MQTT_TOPIC_SUD_DEVICES_ALL = "/Devices/All"
MQTT_TOPIC_SUD_COMSUMTION_METER = "/Meter/Monitor"
# 
ModeSysTemp = "" 
ModeSysTemp_Control = "" 
mode_each_device = 0
device_name=""
status_register_block=[]
status_device=""
device_id=""
msg_device=""
point_list_device=[]
device_control = 0
temp_control = False 
enable_write_control=False
query_device_control=""
query_only_device=""
data_write_device=[]
parameter = []
count = 0 
len_result_topic1 = 0


result_topic1 = []
result_topic2 = []
bitcheck_topic1 = 0

enable_zero_export = 0
value_zero_export_temp = 0
enable_power_limit = 0
value_power_limit = 0

total_wmax = 0
total_wmax_man = 0

# Set time shutdown of inverter
inv_shutdown_enable=False
inv_shutdown_datetime=""
inv_shutdown_point=[]

QUERY_INFORMATION_CONNECT_MODBUS_TCP = ""
QUERY_ALL_DEVICES = ""
QUERY_TYPE_DEVICE = ""
QUERY_REGISTER_DATATYPE = ""
QUERY_DATATYPE = ""


NAME_DEVICE_TYPE=None
ID_DEVICE_TYPE=None
device_mode=None
# 0: Manual mode
# 1: Auto mode
id_template=None
# ----------------------------------------------------------------------
rated_power=None
rated_power_custom=None
rated_power_custom_calculator=None
min_watt_in_percent=None
meter_type=None
start_up_DC_input_voltage=None
operating_DC_input_voltage=None
# 
rated_DC_input_voltage =None
maximum_DC_input_current=None
# 
rated_DC_input_power=None
inverter_type=None
# 

power_limit_percent=None
power_limit_percent_enable=None
reactive_limit_percent=None
reactive_limit_percent_enable=None
rated_reactive_custom=None
device_parent=None
emergency_stop=None
type_device_type=None
# 
# config[0] -- id
# ----- mybatis -----
# mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
#     xml=os.path.abspath(os.getcwd()) + '/mybatis/device_list.xml')
# 

def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
# Describe functions before writing code
# /**
# 	 * @description Definition of point data
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {}
# 	 * @return data {ItemID, Name, Units, Value, Timestamp,Quality}
# 	 */
def point_object(Config,
                 id_point_type,
                 name_point_type,
                 id_point,parent,
                 id,point_key,
                 name,unit,value,
                 quality,timestamp=None,
                 message="", active=0,
                 id_control_group=None,
                 control_type_input=0,
                 control_menu_order=None,
                 control_min=None,
                 control_max=None,
                 control_enabled=1,# show/hide = 1/0, get from Device
                 panel_height=None,
                 panel_width=None,
                 output_values=None,
                 slope=None
                 ):
    modify_value=value
    return {"config":Config,
            "id_point_list_type":id_point_type,
            "name_point_list_type":name_point_type,
            "id_point":id_point,
            "parent":parent,
            "id": id,
            "point_key":point_key,
            "name": name, 
            "unit": unit, 
            "value":  modify_value, 
            "quality":quality,
            "timestamp":(lambda x:  getUTC() if x ==None else x) (timestamp),
            "message":message,
            # "point_type":PointType,
            "active":active,
            "id_control_group":id_control_group,
            "control_type_input":control_type_input,
            "control_menu_order":control_menu_order,
            "control_min":control_min,
            "control_max":control_max,
            "control_enabled":control_enabled,
            "panel_height":panel_height,
            "panel_width":panel_width,
            "output_values":output_values,
            "slope":slope
            }
# Describe functions before writing code
# /**
# 	 * @description Modbus Function Codes
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {client, FUNCTION, ADDRs, COUNT, slave_ID}
# 	 * @return data (registers)
# 	 */
def select_function(client, FUNCTION, ADDRs, COUNT, slave_ID):
    result_rb=None
    while True:
        try:
            
            # match FUNCTION:
            #     case 0:# not used           
            #         return []
            #     case 1:# Read Coils
            #         ADDR = ADDRs                        
            #         result_rb = client.read_coils(
            #                         ADDR, COUNT, unit=slave_ID)

                        
            #         return result_rb

            #     case 2:# Read Discrete Inputs      
            #         ADDR = ADDRs
            #         result_rb = client.read_discrete_inputs(
            #                             ADDR, COUNT, unit=slave_ID)
            #         return result_rb
                
            #     case 3:# Read Holding Registers
            #         ADDR = ADDRs
            #         result_rb = client.read_holding_registers(
            #                             ADDR, COUNT, unit=slave_ID)
            #         return result_rb

            #     case 4:# Read Input Registers
            #         ADDR = ADDRs
            #         result_rb = client.read_input_registers(
            #                             ADDR, COUNT, unit=slave_ID)
            #         return result_rb
            #     case _:
            #         return []
            match FUNCTION:
                case 0:# not used           
                    result_rb = None
                case 1:# Read Coils
                    # 0x
                    ADDR = ADDRs                        
                    result_rb = client.read_coils(
                                    ADDR, COUNT, unit=slave_ID)

                        
                    # return result_rb

                case 2:# Read Discrete Inputs
                    #  1x 
                    ADDR = ADDRs #-10000
                    result_rb = client.read_discrete_inputs(
                                        ADDR, COUNT, unit=slave_ID)
                    # return result_rb
                
                case 3:# Read Holding Registers
                    # 4x
                    ADDR = ADDRs #-40000
                    result_rb = client.read_holding_registers(
                                        ADDR, COUNT, unit=slave_ID)
                    # return result_rb

                case 4:# Read Input Registers
                    # 3x
                    ADDR = ADDRs #-30000
                    result_rb = client.read_input_registers(
                                        ADDR, COUNT, unit=slave_ID)
                    # return result_rb
                case _:
                    result_rb = None
            # 
            # print(f'result_rb: {result_rb}')
            if result_rb==None:
                return {
                    "code":None,
                    "data":[],
                    "exception_code":""
                }
            elif hasattr(result_rb, "function_code"): 
                
                if hasattr(result_rb, "exception_code"):
                    desc=""
                    match result_rb.exception_code:
                        case 1:
                            desc="IllegalFunction"
                        case 2:
                            desc="IllegalAddress"
                        case 3:
                            desc="IllegalValue"
                        case 4:
                            desc="SlaveFailure"
                        case 5:
                            desc="Acknowledge"
                        case 6:
                            desc="SlaveBusy"
                        case 8:
                            desc="MemoryParityError"
                        case 10:
                            desc="GatewayPathUnavailable"
                        case 11:
                            desc="GatewayNoResponse"
                    return {
                        "code":result_rb.function_code,
                        "data":[],
                        "exception_code":desc,
                        "address":ADDR
                    }
                elif hasattr(result_rb, "registers"):
                    return {
                        "code":100,
                        "data":result_rb.registers,
                        "exception_code":"",
                        "address":ADDR
                    }
            
        except Exception as err:
            print(f'Error select_function {err}')
            return {
                    "code":404,
                    "data":[],
                    "exception_code":err
                }

# Describe functions before writing code
# /**
# 	 * @description convert data of register to point list
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {point_list_item,data_of_register}
# 	 * @return data (ItemID, Name, Units, Value, Timestamp,Quality)
# 	 */

def convert_register_to_point_list(point_list_item,data_of_register):
    try:
        point_list={}
        point_value :int = None
        data_have=0
        match point_list_item['pointtype']:
            case "Modbus register":
                datatype=point_list_item['value_datatype']
                match datatype:
                    case 3: # Short Signed 16-bit
                        result = []
                        for itemD in data_of_register:
                            if point_list_item['register'] == itemD["MRA"]and point_list_item['func'] == itemD["func"]:
                                result.append(itemD["Value"])
                        # print(f'result: --- {result}')        
                        if len(result) > 0:
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_16bit_int()
                            data_have=1
                        else:
                            data_have=0
                    case 4: # Word Unsigned 16-bit
                        result = []
                        point_value :int = None
                        for itemD in data_of_register:
                            if point_list_item['register'] == itemD["MRA"] and point_list_item['func'] == itemD["func"]:
                                result.append(itemD["Value"])
                        # print(f'result: --- {result}')        
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_16bit_uint()
                            data_have=1
                        else:
                            data_have=0
                    case 5: # Long Signed 32-bit
                        
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point_list_item['register'])
                        if R1:
                            R2=R1+1
                            Rn.append({
                                "register":R1,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R2,
                                "func":point_list_item['func']
                            })
                        for item in Rn:
                            for itemD in data_of_register:
                                if item["register"] == itemD["MRA"] and item['func'] == itemD["func"]:
                                    result.append(itemD["Value"])      
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_32bit_int()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 6: # DWord Unsigned 32-bit
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point_list_item['register'])
                        if R1:
                            R2=R1+1
                            Rn.append({
                                "register":R1,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R2,
                                "func":point_list_item['func']
                            })
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"] and item['func'] == itemD["func"]:
                                    result.append(itemD["Value"])      
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_32bit_uint()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 7: # LLong Signed 64-bit
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point_list_item['register'])
                        if R1:
                            R2=R1+1
                            R3=R1+2
                            R4=R1+3
                            
                            # Rn.append(R1)
                            # Rn.append(R2)
                            # Rn.append(R3)
                            # Rn.append(R4)
                            Rn.append({
                                "register":R1,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R2,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R3,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R4,
                                "func":point_list_item['func']
                            })
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"] and item['func'] == itemD["func"]:
                                    result.append(itemD["Value"])      
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_64bit_int()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 8: # QWord Unsigned 64-bit 
                        result = []
                        point_value :int = None
                        Rn=[]
                        R1=int(point_list_item['register'])
                        if R1:
                            R2=R1+1
                            R3=R1+2
                            R4=R1+3
                            
                            # Rn.append(R1)
                            # Rn.append(R2)
                            # Rn.append(R3)
                            # Rn.append(R4)
                            Rn.append({
                                "register":R1,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R2,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R3,
                                "func":point_list_item['func']
                            })
                            Rn.append({
                                "register":R4,
                                "func":point_list_item['func']
                            })
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"] and item['func'] == itemD["func"]:
                                    result.append(itemD["Value"])      
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_64bit_uint()
                            
                            data_have=1
                        else:
                            data_have=0
                    case 9: # Float 32-bit real value IEEE-754       
                        
                        result = []
                        point_value : float = None
                        for itemD in data_of_register:
                            if point_list_item['register'] == itemD["MRA"]and point_list_item['func'] == itemD["func"]:
                                result.append(itemD["Value"])
                        for itemD in data_of_register:
                            if point_list_item['register']+1 == itemD["MRA"]and point_list_item['func'] == itemD["func"]:
                                result.append(itemD["Value"])
                        if len(result) > 0:
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_32bit_float()
                            data_have=1
                        else:
                            data_have=0
                    case 10: # Double 64-bit real value
                        return {}
                    case _:
                        return {}
                
                if data_have==0:
                    point_list=point_object(point_list_item['config_information'],
                                                            point_list_item['id_point_list_type'],
                                                            point_list_item['name_point_list_type'],
                                                            point_list_item['id_point'],
                                                            point_list_item['parent'],
                                                            point_list_item['id'],
                                                            point_list_item['pointkey'], 
                                                            point_list_item['point_name'], 
                                                            point_list_item['name_units'], 
                                                            value=point_value, 
                                                            quality=1,
                                                            message="Not found register",
                                                            active=point_list_item['active'],
                                                            id_control_group=point_list_item['id_control_group'],
                                                            control_type_input=point_list_item['control_type_input'],
                                                            control_menu_order=point_list_item['control_menu_order'],
                                                            control_min=point_list_item['control_min'],
                                                            control_max=point_list_item['control_max'],
                                                            control_enabled=1,
                                                            panel_height=point_list_item['panel_height'],
                                                            panel_width=point_list_item['panel_width'],
                                                            output_values=point_list_item['output_values'],
                                                            slope=point_list_item['slope'],
                                                            )
                else:
                    if point_value != None:
                        point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                        point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                        value=None
                        if datatype==9:# Float 32-bit real value IEEE-754    
                            value=round(point_value,2)
                        else:
                            value=func_check_float(point_value)
                        point_list=point_object(point_list_item['config_information'],
                                                point_list_item['id_point_list_type'],
                                                point_list_item['name_point_list_type'],
                                                point_list_item['id_point'],
                                                point_list_item['parent'],
                                                point_list_item['id'], 
                                                point_list_item['pointkey'], 
                                                point_list_item['point_name'], 
                                                point_list_item['name_units'], 
                                                value=value, 
                                                quality=0,
                                                message="",
                                                active=point_list_item['active'],
                                                id_control_group=point_list_item['id_control_group'],
                                                control_type_input=point_list_item['control_type_input'],
                                                control_menu_order=point_list_item['control_menu_order'],
                                                control_min=point_list_item['control_min'],
                                                control_max=point_list_item['control_max'],
                                                control_enabled=1,
                                                panel_height=point_list_item['panel_height'],
                                                panel_width=point_list_item['panel_width'],
                                                output_values=point_list_item['output_values'],
                                                slope=point_list_item['slope'],
                                                )
                return point_list
            case "Internal":
                point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point_list_type'],
                                        point_list_item['name_point_list_type'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                        point_list_item['id'], 
                                        point_list_item['pointkey'], 
                                        point_list_item['point_name'], 
                                        point_list_item['name_units'], 
                                        value=None, 
                                        quality=0,
                                        message="",
                                        active=point_list_item['active'],
                                        id_control_group=point_list_item['id_control_group'],
                                        control_type_input=point_list_item['control_type_input'],
                                        control_menu_order=point_list_item['control_menu_order'],
                                        control_min=point_list_item['control_min'],
                                        control_max=point_list_item['control_max'],
                                        control_enabled=1,
                                        panel_height=point_list_item['panel_height'],
                                        panel_width=point_list_item['panel_width'],
                                        output_values=point_list_item['output_values'],
                                        slope=point_list_item['slope'],
                                        )
                return point_list
            case "Equation":
                point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point_list_type'],
                                        point_list_item['name_point_list_type'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                        point_list_item['id'], 
                                        point_list_item['pointkey'], 
                                        point_list_item['point_name'], 
                                        point_list_item['name_units'], 
                                        point_list_item['constants'], 
                                        quality=0,
                                        message="",
                                        active=point_list_item['active'],
                                        id_control_group=point_list_item['id_control_group'],
                                        control_type_input=point_list_item['control_type_input'],
                                        control_menu_order=point_list_item['control_menu_order'],
                                        control_min=point_list_item['control_min'],
                                        control_max=point_list_item['control_max'],
                                        control_enabled=1,
                                        panel_height=point_list_item['panel_height'],
                                        panel_width=point_list_item['panel_width'],
                                        output_values=point_list_item['output_values'],
                                        slope=point_list_item['slope'],
                                        )
                return point_list
        
    except Exception as err:
        print(f'Error convert_register_to_point_list {err}')
        return {}
# Describe functions before writing code
# /**
# 	 * @description write modbus to device
# 	 * @author vnguyen
# 	 * @since 15-11-2023
# 	 * @param {client, unit, datatype,register, value}
# 	 * @return data (msg)
# 	 */   
def write_modbus_tcp(client, unit=None, datatype=None, modbus_func=None,register=None, value=None):
    try:
        print(f'datatype: {datatype}|modbus_func: {modbus_func}')
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
        match modbus_func:
            case 1:
                result = client.write_coils(
                address, [value], skip_encode=True, unit=unit)
                if hasattr(result, "function_code"):
                    print(f'result: {result.function_code }')
                    if result.function_code == 15:
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
            case 3:
                result = client.write_registers(
                address, payload, skip_encode=True, unit=unit)
                if hasattr(result, "function_code"):
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
            case 5:
                result = client.write_coils(
                address,  [value], skip_encode=True, unit=unit)
                if hasattr(result, "function_code"):
                    print(f'result: {result.function_code }')
                    if result.function_code == 15:
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
def func_slope(slopeenabled,slope,Value): #multiply by constant
    result= None
    if slopeenabled==1:
        result=Value*slope
    else:
        result=Value
    return result
def func_Offset(offsetenabled,offset,Value): #add constant
    result= None
    if offsetenabled==1:
        result=Value+offset
    else:
        result=Value
    return result
def func_check_float(Value): #Check if a number is int or float
    result= None
    if type(Value) == float:
        result=round(Value,2)
    else:
        result=Value
    return result
def func_check_data_mybatis(data,item,object_name):
    try:
        
        if data[item].get(object_name):
           return data[item].get(object_name)
        else:
            return ""
        
    except Exception as err:
      print('Error not find object mybatis')
      return ""

# ----- MQTT -----
# Describe functions before writing code
# /**
# 	 * @description public data MQTT
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {host, port,topic, username, password, data_send}
# 	 * @return data ()
# 	 */
def func_mqtt_public(host, port,topic, username, password, data_send):
    try:
        payload = json.dumps(data_send)
        # client_id= datetime.datetime.now(datetime.timezone.utc).strftime(
        #                     "%Y%m%d_%H%M%S"
        #                 )
        publish.single(topic, payload, hostname=host,
                    #    client_id=str(client_id),
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
def path_directory_relative(project_name):
    if project_name =="":
      return -1
    path_os=os.path.dirname(__file__)
    # print("Path os:", path_os)
    string_find=project_name
    index_os = path_os.find(string_find)
    if index_os <0:
      return -1
    result=path_os[0:int(index_os)+len(string_find)]
    # print("Path directory relative:", result)
    return result
# Describe check_inverter_device 
# 	 * @description check_inverter_device
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {device_control}
# 	 * @return Device is inverter 
# 	 */ 
async def check_inverter_device(device_control):
    results_device_type = []
    
    query = "SELECT `device_type`.`name` FROM device_type INNER JOIN `device_list` ON device_list.id_device_type=device_type.id WHERE device_list.id=%s;"
    results_device_type = MySQL_Select(query, (device_control,))
    if results_device_type and results_device_type[0]["name"] == "PV System Inverter":
        return True  
    else:
        return False  
# Describe find_inverter_information 
# 	 * @description find_inverter_information
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {device_control , parameter}
# 	 * @return value , register , datatype , id_point_key 
# 	 */ 
async def find_inverter_information(device_control, parameter):
    # query_register = """SELECT id_pointkey, register, id_type_datatype 
    #                     FROM point_list INNER JOIN device_list ON device_list.id_template = point_list.id_template 
    #                     WHERE device_list.id = %s;"""
    query_register = """SELECT id_pointkey, point_list.register, point_list.id_type_datatype ,table_type_function.value AS modbus_func
                        FROM device_point_list_map 
                        INNER JOIN point_list ON device_point_list_map.id_point_list = point_list.id 
                        LEFT JOIN config_information table_type_function ON point_list.id_type_function=table_type_function.id
                        WHERE device_point_list_map.id_device_list = %s;"""
    query_datatype = "SELECT value FROM config_information WHERE id = %s"
    # Get the id_pointkey on message to get information in the database
    results_register = MySQL_Select(query_register, (device_control,))
    inverter_information = [item for item in results_register if item['id_pointkey'] in [p['id_pointkey'] for p in parameter]]
    # update datatype for result
    for item in inverter_information:
        item.update({"value": next((p["value"] for p in parameter if p["id_pointkey"] == item["id_pointkey"]), None)})
        item["datatype"] = MySQL_Select(query_datatype, (item["id_type_datatype"],))[0]["value"] if MySQL_Select(query_datatype, (item["id_type_datatype"],)) else None
    return inverter_information
# Describe write_device_tcp
# 	 * @description write_device
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {ConfigPara ,client ,slave_ID , serial_number_project , mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password}
# 	 * @return results_write_modbus
# 	 */ 
async def write_device(
    ConfigPara ,
    client ,
    slave_ID , 
    serial_number_project , 
    mqtt_host, 
    mqtt_port, 
    topicPublic, 
    mqtt_username, 
    mqtt_password
    )-> None:
    # Args:
    #     config_para (dict): Configuration parameters.
    #     client (object): Modbus TCP client.
    #     slave_id (int): Slave ID.
    #     serial_number_project (str): Serial number of the project.
    #     mqtt_host (str): MQTT host.
    #     mqtt_port (int): MQTT port.
    #     topic_public (str): Public topic for MQTT.
    #     mqtt_username (str): MQTT username.
    #     mqtt_password (str): MQTT password.
    # Global Variables
    global device_mode # mode of device
    global status_device # status of device
    global rated_power # rated_power
    global rated_power_custom # rated_power_custom
    global power_limit_percent
    global power_limit_percent_enable
    global reactive_limit_percent
    global reactive_limit_percent_enable
    global rated_reactive_custom
    global result_topic1 # result topic 
    global mode_each_device
    # Local Variables
    
    # Get Id_Systemp
    topicPublic = serial_number_project + topicPublic
    id_systemp = ConfigPara[1]
    id_systemp = int(id_systemp)
    
    # result Modbus
    results_write_modbus = []
    parameter_temp = [] 
    inverter_info_temp = []
    result_slope = []
    result_slope_wmax = []
    
    # information Modbus 
    register = ""
    datatype = ""
    id_pointkey = ""
    code_value = 0
    slope = 1.0
    slope_wmax = 1.0
    value_convert_reactive_percent = 0
    # mqtt
    comment = 200
    current_time = get_utc()
    data_send = ""
    
    # database
    is_inverter = []
    inverter_info = []
    inverter_info_temp = []
    result_query_findname = []
    name_device_points_list_map = ""
    
    if result_topic1 :
        for item in result_topic1:
            device_control = item['id_device']
            device_control = int(device_control) # Get Id_device from message mqtt
            if id_systemp == device_control :
                parameter = item['parameter']
                print("result_topic1",result_topic1)
                print("parameter",parameter)
                if parameter :
                    print("---------- write data from Device ----------")
                    try:
                        # Check Id is INV
                        if device_control : 
                            is_inverter = await check_inverter_device(device_control)
                        else :
                            pass
                        # Get information INV from Id_device
                        if is_inverter: 
                            inverter_info = await find_inverter_information(device_control, parameter)
                            print("inverter_info",inverter_info)
                            # Scan message mqtt get information register
                            for item in inverter_info: 
                                value = item["value"]
                                register = item["register"]
                                id_pointkey = item['id_pointkey']
                                datatype = item["datatype"]
                                modbus_func= item["modbus_func"]
                                result_query_findname = MySQL_Select('select `name` from `point_list` where `register` = %s and `id_pointkey` = %s', (register,id_pointkey,))
                                name_device_points_list_map = result_query_findname [0]["name"]
                                # Man Mode
                                if device_mode == 0 and value != None: 
                                    print("---------- Manual control mode ----------")
                                    addtopic = "Feedback"
                                    if len(inverter_info) == 1 and parameter[0]['id_pointkey'] == "ControlINV": # Control On/Off INV 
                                        if value == True :
                                            results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, modbus_func, register, value=1)
                                            MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(1,device_control,name_device_points_list_map))
                                        elif value == False :
                                            results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, modbus_func,register, value=0)
                                            MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(0,device_control,name_device_points_list_map))
                                    if len(inverter_info) >= 1 and (isinstance(value, int) or isinstance(value, float)): # Control Parameter INV
                                        id_pointkey = str(id_pointkey)
                                        result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`id_pointkey` = %s AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s", (id_pointkey, id_systemp,))
                                        # convert back to actual value
                                        if result_slope and slope :
                                            slope = float(result_slope[0]['slope'])
                                            if power_limit_percent_enable == 1:
                                                result_slope_wmax = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`id_pointkey` = 'WMax' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s", (id_systemp,))
                                                if result_slope_wmax:
                                                    slope_wmax = float(result_slope_wmax[0]['slope'])
                                                    parameter_temp = [{'id_pointkey': 'WMax', 'value': rated_power_custom_calculator*(power_limit_percent/100) / slope_wmax}]
                                                    inverter_info_temp = await find_inverter_information(device_control, parameter_temp)
                                                    if inverter_info_temp and inverter_info_temp[0]["register"] and inverter_info_temp[0]["datatype"]:
                                                        write_modbus_tcp(client, slave_ID, inverter_info_temp[0]["datatype"],
                                                                        inverter_info_temp[0]["modbus_func"],
                                                                        inverter_info_temp[0]["register"], value=inverter_info_temp[0]["value"])
                                                        
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (power_limit_percent_enable, device_control, 'Power Limit Percent Enable'))
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (power_limit_percent, device_control, 'Power Limit Percent'))
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (rated_power_custom_calculator*(power_limit_percent/100), device_control, 'Power Limit'))
                                            if reactive_limit_percent_enable == 1:
                                                result_slope_wmax = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`id_pointkey` = 'WMax' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s", (id_systemp,))
                                                if result_slope_wmax:
                                                    slope_wmax = float(result_slope_wmax[0]['slope'])
                                                    if rated_reactive_custom is not None and reactive_limit_percent is not None:
                                                        value_convert_reactive_percent = rated_reactive_custom*(reactive_limit_percent/100)
                                                        parameter_temp = [{'id_pointkey': 'VarMax', 'value': value_convert_reactive_percent/ slope_wmax}]
                                                        inverter_info_temp = await find_inverter_information(device_control, parameter_temp) 
                                                    if inverter_info_temp and inverter_info_temp[0]["register"] and inverter_info_temp[0]["datatype"]:
                                                        write_modbus_tcp(client, slave_ID, inverter_info_temp[0]["datatype"],
                                                                        inverter_info_temp[0]["modbus_func"],
                                                                        inverter_info_temp[0]["register"], value=inverter_info_temp[0]["value"])
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (reactive_limit_percent_enable, device_control, 'Reactive Power Limit Percent Enable'))
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (reactive_limit_percent, device_control, 'Reactive Power Limit Percent'))
                                                        MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (value_convert_reactive_percent, device_control, 'Reactive Power Limit'))
                                            if id_pointkey in [ "WMax", "WMaxPercent","WMaxPercentEnable","VarMax","VarMaxPercent","VarMaxPercentEnable","PFSet","PFSetEnable"]:
                                                MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s', (value, device_control, name_device_points_list_map))
                                                if slope is not None and slope != 0:
                                                    value /= slope
                                            # Write down the inv value after conversion
                                            results_write_modbus = write_modbus_tcp(client, slave_ID, datatype,modbus_func, register, value=value)
                                # Auto Mode
                                if device_mode == 1 and any('status' in item for item in result_topic1):
                                    print("---------- Auto control mode ----------")
                                    addtopic = "FeedbackAuto"
                                    if len(inverter_info) >= 1 and (isinstance(value, int) or isinstance(value, float)):# Control Auto On/Off and Write parameter to INV
                                        result_slope = MySQL_Select("SELECT `point_list`.`slope` FROM point_list JOIN device_list ON point_list.id_template = device_list.id_template AND `point_list`.`id_pointkey` = 'WMax' AND `point_list`.`slopeenabled` = 1 WHERE `device_list`.id = %s", (id_systemp,))
                                        # convert back to actual value
                                        if result_slope and slope and id_pointkey == 'WMax' :
                                            slope = float(result_slope[0]['slope'])
                                            value = value/slope
                                        results_write_modbus = write_modbus_tcp(client, slave_ID, datatype,modbus_func, register, value=value)
                            # check fault push the results to mqtt
                            if results_write_modbus: # Code that writes data to the inverter after execution 
                                code_value = results_write_modbus['code']
                                
                                if code_value == 16 :
                                    comment = 200
                                    mode_each_device = device_mode
                                else:
                                    comment = 400
                                    device_mode = mode_each_device
                                
                            data_send = {
                                "time_stamp": current_time,
                                "status": comment,
                            }
                            mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublic + "/" + addtopic, mqtt_username, mqtt_password, data_send)
                            result_topic1 = []
                    except Exception as err:
                        print(f"write_device: '{err}'")
                # check data change mode device action
                elif len(parameter) == 0 :
                    data_send = {
                                "time_stamp": current_time,
                                "status": 200,
                            }
                    mqtt_public_paho_zip(mqtt_host, mqtt_port, topicPublic + "/" + "Feedbacksetup", mqtt_username, mqtt_password, data_send)
                    result_topic1 = []
# Describe functions before writing code
# /**
# 	 * @description read modbus TCP
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {id_device, path (source run file python)}
# 	 * @return data ()
# 	 */
async def device(serial_number_project,ConfigPara,mqtt_host,
                            mqtt_port,
                            topicPublic,
                            mqtt_username,
                            mqtt_password):
    try:
        
        if len(ConfigPara)>=2 and type(ConfigPara) == list :
            pass
        else:
            return -1
        global query_device_control,query_only_device
        # global data_control
        global inv_shutdown_enable,inv_shutdown_datetime,inv_shutdown_point
        global device_id
        global device_mode
        global id_template
        global power_limit_percent,power_limit_percent_enable,reactive_limit_percent,reactive_limit_percent_enable
        global type_device_type
        pathSource=path
        print(f'pathSource: {pathSource}')
        # pathSource="D:/NEXTWAVE/project/ipc_api"
        id_device=ConfigPara[1]
        device_id = id_device
        # mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
        # xml=pathSource + '/mybatis/device_list.xml')
        # statement = mybatis_mapper2sql.get_statement(
        # mapper, result_type='list', reindent=True, strip_comments=True) 
        # 
        # query_all= func_check_data_mybatis(statement,0,"select_all_device")
        # query_only_device=func_check_data_mybatis(statement,1,"select_only_device")
        # query_point_list=func_check_data_mybatis(statement,2,"select_point_list")
        # query_register_block=func_check_data_mybatis(statement,3,"select_register_block")
        
        # query_device_control=func_check_data_mybatis(statement,4,"select_device_control")
        # if query_all != -1 and query_only_device  != -1 and query_point_list  != -1 and query_register_block  != -1:
        #     pass
        # else:           
        #     print("Error not found data in file mybatis")
        #     return -1
        # # 
        query_only_device=device_query.select_only_device_use_driver.format(id_device=id_device)
        results_device =await MySQL_Select_v1(query_only_device)
        # 
        if type(results_device) == list and len(results_device)>=1:
            pass
        else:           
            print("Error not found data device")
            return -1
        id_template=results_device[0]["id_template"]
        # 
        query_point_list=device_query.select_point_list.format(id_device=id_device)
        query_register_block=device_query.select_register_block.format(id_template=id_template)
        # 
        results_RBlock=await MySQL_Select_v1(query_register_block)
        results_default_Plist=await MySQL_Select_v1(query_point_list)
        # Check the register Modbus
        if type(results_RBlock) == list and len(results_RBlock)>=1:
            pass
        else:           
            print("Error device register not found")
            # return -1
        # Check the point list Modbus
        if type(results_default_Plist) == list and len(results_default_Plist)>=1:
            pass
        else:           
            print("Error device point list not found")
            # return -1
        # results_Plist=results_default_Plist
        results_Plist=[]
        if results_default_Plist:
            for itemP in results_default_Plist:
                match itemP["pointkey"]:
                    case "WMaxPercent":
                        power_limit_percent=int(itemP["output_values"])
                    case "WMaxPercentEnable":
                        power_limit_percent_enable=int(itemP["output_values"])
                    case "VarMaxPercent":
                        reactive_limit_percent=int(itemP["output_values"])
                    case "VarMaxPercentEnable":
                        reactive_limit_percent_enable=int(itemP["output_values"])
                    case _:
                        pass
                results_Plist.append({**itemP})
        # inv_shutdown_enable=results_device[0]["enable_poweroff"]
        device_mode=results_device[0]['mode']
        global rated_power
        global rated_power_custom
        global rated_power_custom_calculator
        global min_watt_in_percent
        global meter_type
        global rated_DC_input_voltage
        global maximum_DC_input_current
        global inverter_type
        global device_parent
        global emergency_stop
        if results_device[0]['rated_power']!=None:
            rated_power=results_device[0]['rated_power']
            rated_power_custom_calculator=results_device[0]['rated_power']
            
        if results_device[0]['rated_power_custom']!=None:
            rated_power_custom=results_device[0]['rated_power_custom']
            
        if results_device[0]['min_watt_in_percent']!=None:
            min_watt_in_percent=results_device[0]['min_watt_in_percent']

        rated_DC_input_voltage=results_device[0]['DC_voltage']
        maximum_DC_input_current=results_device[0]['DC_current']
        
        meter_type=results_device[0]['meter_type']
        inverter_type =results_device[0]['inverter_type']
        device_parent=results_device[0]['device_parent']
        emergency_stop=results_device[0]['emergency_stop']
        type_device_type=results_device[0]['type_device_type']
        while True:
                # Share data to Global variable
                global status_device
                global device_name,msg_device
                global point_list_device,status_register_block
                global enable_write_control
                global data_write_device
                global NAME_DEVICE_TYPE
                global ID_DEVICE_TYPE
                
                
                device_name=results_device[0]["name"]
                slave_ip = results_device[0]["tcp_gateway_ip"]
                slave_port = results_device[0]['tcp_gateway_port']
                slave_ID =  results_device[0]['rtu_bus_address']
                NAME_DEVICE_TYPE =  results_device[0]['device_type']
                ID_DEVICE_TYPE =  results_device[0]['id_device_type']
                

                
                try:
                    print(f'-----{getUTC()} Read data from Device -----')
                    with ModbusTcpClient(slave_ip, port=slave_port) as client:
                    # client =ModbusTcpClient(slave_ip, port=slave_port)
                    # connection = client.connect()
                    # if connection:

                        await write_device(ConfigPara,client,slave_ID ,serial_number_project , mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password)
                        # await asyncio.sleep(1)
                        # print("---------- read data from Device ----------")

                        msg_device=""
                        # 
                        Data = []
                        status_rb=[]
                        status_register_block=[]
                        for itemRB in results_RBlock:
                            # await asyncio.sleep(0.5)
                            FUNCTION = itemRB["Functions"]
                            ADDR = itemRB["addr"]
                            COUNT = itemRB["count"]
                            result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ID)
                            # print(f'result_rb: {result_rb}')
                            match result_rb["code"]:
                                case None:
                                    status_device="offline"
                                case 404:
                                    status_device="offline"
                                case 131:
                                    exception_code=result_rb["exception_code"]
                                    if exception_code=="GatewayNoResponse":
                                        status_device="offline"
                                        
                                        status_rb.append({"ADDR":ADDR,
                                                        "ERROR_CODE":139,
                                                        "Timestamp": getUTC(),
                                                        })
                                    else:
                                        status_device="online"
                                        status_rb.append({"ADDR":ADDR,
                                                        "ERROR_CODE":exception_code,
                                                        "Timestamp": getUTC(),
                                                        })
                                    # print(f'ERROR CODE: {result_rb["exception_code"]}')
                                    print(f"Error reading from {slave_ip}: {result_rb}")
                                    # status_register_block=status_rb
                                    
                                case 100:
                                    status_device="online"
                                    INC = ADDR-1
                                    for itemR in result_rb["data"]:
                                        INC = INC+1
                                        Data.append({"MRA": INC, "Value": itemR,"func":FUNCTION })
                        new_Data = [x for i, x in enumerate(Data) if x['MRA'] not in {y['MRA'] for y in Data[:i]}]
                        # 
                        # for item_rb in status_rb:
                        #     for item_rbs in status_register_block:
                        #         if status_register_block:
                        #             if 'ERROR_CODE' in status_register_block[0].keys():
                        #                 error_code=status_register_block[0]["ERROR_CODE"]
                        #                 if error_code==139:
                        #                     status_register_block[0]={"ADDR":ADDR,
                        #                                     "ERROR_CODE":exception_code,
                        #                                     "Timestamp": getUTC(),
                        #                         }
                                            
                                        
                        # 
                        point_list = []
                        for itemP in results_Plist:
                            result= convert_register_to_point_list(itemP,new_Data)
                            if result:
                                point_list.append(result)
                            else:
                                pass
                        #    
                        point_list_device=point_list
                        
                        # 
                        await asyncio.sleep(5)
                        # 
                        client.close()
                except (ConnectionException, ModbusException) as e:
                    status_device="offline"
                    print(f"Modbus error from {slave_ip}: {e}")
                    msg_device=f"{slave_ip}: {e}"
                    point_list_error=[]
                    # if point_list_device:
                    #     print(point_list_device[0])
                    
                    if point_list_device:
                        for item in point_list_device:
                            point_list_error.append(point_object(
                                                item['config'],
                                                item['id_point_list_type'],
                                                item['name_point_list_type'],
                                                item['id_point'],
                                                item['parent'],
                                                item['id'], 
                                                item['point_key'],
                                                item['name'], 
                                                item['unit'], 
                                                item['value'], 
                                                1,
                                                item['timestamp'],
                                                message="Error Device",
                                                active=item['active'],
                                                id_control_group=item['id_control_group'],
                                                control_type_input=item['control_type_input'],
                                                control_menu_order=item['control_menu_order'],
                                                control_min=item['control_min'],
                                                control_max=item['control_max'],
                                                control_enabled=item['control_enabled'],
                                                panel_height=item['panel_height'],
                                                panel_width=item['panel_width'],
                                                output_values=item['output_values'],
                                                slope=item['slope'],
                                                ))
                    else:
                        
                        for item in results_Plist:
                            point_list_error.append(
                                point_object(
                                                item['config_information'],
                                                item['id_point_list_type'],
                                                item['name_point_list_type'],
                                                item['id_point'],
                                                item['parent'],
                                                item['id'], 
                                                item['pointkey'],
                                                item['point_name'], 
                                                item['name_units'], 
                                                None, 
                                                1,
                                                None,
                                                message="error device",
                                                active=item['active'],
                                                id_control_group=item['id_control_group'],
                                                control_type_input=item['control_type_input'],
                                                control_menu_order=item['control_menu_order'],
                                                control_min=item['control_min'],
                                                control_max=item['control_max'],
                                                control_enabled=1,
                                                panel_height=item['panel_height'],
                                                panel_width=item['panel_width'],
                                                output_values=item['output_values'],
                                                slope=item['slope'],
                                                )
                            )
                        
                    point_list_device=point_list_error
                    await asyncio.sleep(5)
                except AttributeError as ae:
                    print("AE ERROR", ae)
                    await asyncio.sleep(5)
    except KeyError as err:
        print('KeyError device : ', err)
    except Exception as err:
        print('Exception device : ', err)
        
        # raise Exception("Runtime Error!!!") 
    # finally:
    #     print ("--Finally--")      
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(point_type,serial_number_project,host=[], port=[], username=[], password=[]
                        ):
    try:
        global id_template
        global rated_DC_input_voltage
        global maximum_DC_input_current
        global inverter_type
        global device_parent
        global type_device_type
        results_control_group = MySQL_Select(f'SELECT * FROM point_list_control_group where id_template={id_template} and status=1', ())
        print(f'init monitoring_device')
        # point_list
        # 1: Number, 2: String, 3: Percent, 4: Bool
        # point_list_control_group
        # 0=Independent, 1=Depends one, 2=Depends two
        mqtt_init=mqttService(host[0],
                    port[0],
                    username[0],
                    password[0],
                    serial_number_project)
        
        while True:
            print(f'-----{getUTC()} monitoring_device -----')
            process = psutil.Process(os.getpid())
            # print(f'memory: {process.memory_percent()}')
            memory=round(process.memory_percent(),2)
            global device_name,status_device,msg_device,status_register_block,point_list_device
            global power_limit_percent,power_limit_percent_enable,reactive_limit_percent,reactive_limit_percent_enable
            global device_id
            global NAME_DEVICE_TYPE
            global ID_DEVICE_TYPE
            global device_mode
            global rated_power
            global rated_power_custom_calculator
            global rated_power_custom
            global min_watt_in_percent
            global meter_type
            global rated_reactive_custom
            global emergency_stop
            new_point=[]
            mppt=[]
            control_group=[]
            # 
            monitor_service_init=monitoring_service.MonitorService(id_template,rated_DC_input_voltage,maximum_DC_input_current,device_parent,
                device_id,device_name,status_device,msg_device,status_register_block,point_list_device,
                power_limit_percent,power_limit_percent_enable,reactive_limit_percent,reactive_limit_percent_enable,
                name_device_type=NAME_DEVICE_TYPE,
                id_device_type=ID_DEVICE_TYPE,
                device_mode=device_mode,
                rated_power=rated_power,
                rated_power_custom=rated_power_custom,
                min_watt_in_percent=min_watt_in_percent,
                # rated_reactive_custom=rated_reactive_custom,
                meter_type=meter_type,inverter_type=inverter_type)

            device_mode=monitor_service_init.device_type()
            if results_control_group:
                control_group=[
                    {
                        "id":item["id"],
                        "name":item["name"],
                        "description":item["description"],
                        "attributes":item["attributes"],
                        "fields":[]
                        
                    } for item in results_control_group]
            new_point_list_device=monitor_service_init.point_list_change_para_control()
            rated_reactive_custom=monitor_service_init.rated_reactive_custom
            if new_point_list_device:
                for point_item in new_point_list_device:
                    if point_item['config']=="MPPT":
                        mppt_strings=[]
                        mppt_volt=[]
                        mppt_amps=[]                 
                        mppt_volt=[item for item in new_point_list_device if item['parent'] == point_item["id_point"] and item['config'] =="MPPTVolt" ]
                        mppt_amps=[item for item in new_point_list_device if item['parent'] == point_item["id_point"]and item['config'] =="MPPTAmps"]
                        mppt_string=[item for item in new_point_list_device if item['parent'] == point_item["id_point"]and item['config'] =="StringAmps"]
                        number_mppt_panel=0
                        for item_string in mppt_string:
                            mppt_string_panel=[item for item in new_point_list_device if item['parent'] == item_string["id_point"]and item['config'] =="Panel"]
                            area=0
                            number_panel=0
                            # print(mppt_string_panel)
                            if mppt_string_panel:
                                for item_panel in mppt_string_panel:
                                    if item_panel["panel_height"]!=None and item_panel["panel_width"] !=None:
                                        area=area+(item_panel["panel_height"]/1000*item_panel["panel_width"]/1000)
                                number_panel=len(mppt_string_panel)
                                number_mppt_panel=number_mppt_panel+number_panel
                            mppt_strings.append({
                                "point_key":item_string["point_key"],
                                "name":item_string["name"],
                                "value":item_string["value"],
                                "area":area,
                                "number_panel": number_panel,
                                            })
                        
                        Quality=[]
                        if mppt_volt:
                            volt_quality=  [item for item in mppt_volt if item['quality'] == 1]
                            if volt_quality==[]:
                                Quality.append(0)
                            else:
                                Quality.append(1)
                        if mppt_amps:
                            amps_quality=  [item for item in mppt_amps if item['quality'] == 1]
                            if amps_quality==[]:
                                Quality.append(0)
                            else:
                                Quality.append(1)
                        if mppt_string:
                            string_quality=  [item for item in mppt_string if item['quality'] == 1]
                            if string_quality==[]:
                                Quality.append(0)
                            else:
                                Quality.append(1)
                        
                        power =0
                        total_area_string=0
                        irradiance=0
                        if mppt_volt and mppt_amps:
                            pass
                            mppt_v=(lambda x: x[0]['value'] if x else None)(mppt_volt)
                            mppt_a=(lambda x: x[0]['value'] if x else None)(mppt_amps)

                            if mppt_v!= None and mppt_a!=None:
                                power =mppt_v*mppt_a
                        
                        if mppt_strings:
                            for item in mppt_strings:
                                if item["value"]!=None and item["area"]!=0 and item["value"]!=0:
                                    total_area_string=total_area_string+item["area"]
                        if power>0 and total_area_string>0:
                            irradiance=power/total_area_string
                        mppt_item={
                                "config":point_item["config"],
                                "id_point":point_item["id_point"],
                                "parent":point_item["parent"],
                                "id": point_item["id"],
                                "point_key":point_item["point_key"],
                                "name": point_item["name"],
                                "power":round(power,2)/1000,
                                "area":round(total_area_string,2),
                                "irradiance":round(irradiance,2),
                                "number_panel":number_mppt_panel,
                                "DC_voltage_max":rated_DC_input_voltage,
                                "DC_current_max":maximum_DC_input_current,
                                'value':{
                                    "mppt_volt":(lambda x: x[0]['value'] if x else None)(mppt_volt),
                                    "mppt_amps":(lambda x: x[0]['value'] if x else None)(mppt_amps),
                                    "mppt_string":mppt_strings
                                    },
                                "timestamp":getUTC(),
                                "quality":(lambda x: 1 if 1 in Quality else 0)(Quality),
                                }
                        new_point.append(mppt_item)
                        mppt.append(mppt_item)
                    elif point_item['config']=="Field":
                        new_point.append(point_item)
                        pass
                    elif point_item['config']=="Panel":
                        new_point.append(point_item)
                    else:
                        new_point.append(point_item)
            parameters=[]
            for item_type in point_type:
                new_point_type=[]
                for item_point in new_point_list_device:
                    if int(item_type["id"])==int(item_point["id_point_list_type"]):
                        if  item_point["id"]>=0:
                            new_point_type.append({
                                **item_point
                            })
                parameters.append({
                    "id": item_type['id'],
                    "name": item_type['name'],
                    "fields": new_point_type
                })
            new_control_group=[]
            for item_group in control_group:
                new_point_control=[]
                for point_item in new_point_list_device:
                    if point_item["id_control_group"]==item_group["id"]:
                        new_point_control.append({
                            **point_item
                        })
                new_point_control.sort(key=lambda x: x["control_menu_order"])
                new_point_control_attr=[]
                
                match item_group["attributes"]:
                    case 0:
                        for item_point_attr in new_point_control:
                            new_point_control_attr.append(
                                {
                                    **item_point_attr,
                                    "control_enabled":1
                                }
                            )
                    case 1: 
                        if len(new_point_control)==2:
                            control_enable=(lambda x:  x[0]["value"] if x else None) ([item for item in new_point_control if item['control_type_input'] == 4])
                            if control_enable!=None and control_enable!="null":
                                for item_point_attr in new_point_control:
                                    if item_point_attr['control_type_input'] == 4:
                                        new_point_control_attr.append(
                                            {
                                                **item_point_attr,
                                                "control_enabled":1
                                            }
                                        )
                                    else:
                                        new_point_control_attr.append(
                                            {
                                                **item_point_attr,
                                                "control_enabled":(lambda x: 1  if x==1 else 0)(control_enable)
                                            }
                                        )
                            else:
                                for item_point_attr in new_point_control:
                                    new_point_control_attr.append(
                                            {
                                                **item_point_attr,
                                                "control_enabled":1
                                            }
                                        )
                    case 2:  
                        if len(new_point_control)==3:                   
                            control_enable=(lambda x:  x[0]["value"] if x else None) ([item for item in new_point_control if item['control_type_input'] == 4])
                            if control_enable!=None and control_enable!="null":
                                    for item_point_attr in new_point_control:
                                        if item_point_attr['control_type_input'] == 4:
                                            new_point_control_attr.append(
                                                {
                                                    **item_point_attr,
                                                    "control_enabled":1
                                                }
                                            )
                                        elif item_point_attr['control_type_input'] == 1:
                                            new_point_control_attr.append(
                                                {
                                                    **item_point_attr,
                                                    "control_enabled":(lambda x: 1  if x==0 else 0)(control_enable)
                                                }
                                            )
                                        elif item_point_attr['control_type_input'] == 3:
                                            new_point_control_attr.append(
                                                {
                                                    **item_point_attr,
                                                    "control_enabled":(lambda x: 1  if x==1 else 0)(control_enable)
                                                }
                                            )
                            else:
                                    for item_point_attr in new_point_control:
                                        new_point_control_attr.append(
                                                {
                                                    **item_point_attr,
                                                    "control_enabled":1
                                                }
                                            )
                
                new_control_group.append({
                    **item_group,
                    "fields":new_point_control_attr
                })
            combiner_box=monitor_service_init.combiner_box(new_point)
            
            data_device={
                "memory":memory,
                "id_device":device_id,
                "parent":device_parent,
                "mode":device_mode,
                "device_name":device_name,
                "id_device_type":ID_DEVICE_TYPE,
                "name_device_type":NAME_DEVICE_TYPE,
                "type_device_type":type_device_type,
                "meter_type":meter_type,
                "inverter_type":inverter_type,
                "status_device":status_device,
                "timestamp":getUTC(),
                "message":msg_device,
                "status_register":status_register_block,
                "point_count":len(new_point),
                "parameters":parameters,
                "fields":new_point,
                "mppt":mppt,
                "combiner_box":combiner_box,
                "control_group":new_control_group,
                "rated_power":rated_power,# realtime
                "rated_power_custom":rated_power_custom,# realtime
                "min_watt_in_percent":min_watt_in_percent,# realtime
                "rated_reactive_custom":rated_reactive_custom, # realtime
                "emergency_stop":emergency_stop,# realtime
                
            }
            if device_name !="" and serial_number_project!= None:
                # func_mqtt_public(   host[0],
                #                     port[0],
                #                     serial_number_project+"/"+"Devices/"+""+device_id,
                #                     username[0],
                #                     password[0],
                #                     data_device)
                await mqtt_init.sendZIP("Devices/"+""+device_id,
                                        data_device)
            await asyncio.sleep(1)
    except Exception as err:
        print('Error monitoring_device : ',err)
        
    #   return -1
# Describe process_update_mode_for_device
# /**
# 	 * @description process_update_mode_for_device
# 	 * @author bnguyen
# 	 * @since 02-05-2024
# 	 * @param {mqtt_result,serial_number_project,host, port, username, password}
# 	 * @return MySQL_Insert (device_mode, id_device)
# 	 */

async def process_update_mode_for_device(mqtt_result, serial_number_project, host, port, username, password):
    # Global variables
    global device_mode
    global arr
    # Local variables
    id_systemp = arr[1]
    id_systemp = int(id_systemp)
    # Switch to user mode that is both man and auto
    if mqtt_result and all(item.get('id_device') != 'Systemp' for item in mqtt_result):
        for item in mqtt_result:
            id_device = int(item["id_device"])
            checktype_device = MySQL_Select("SELECT device_type.name FROM device_list JOIN device_type ON device_list.id_device_type = device_type.id WHERE device_list.id = %s;", (id_device,))[0]["name"]
            if checktype_device == "PV System Inverter":
                if id_device == id_systemp:
                    device_mode = int(item["mode"])
                    if device_mode in [0, 1]:
                        MySQL_Insert_v5("UPDATE device_list SET device_list.mode = %s WHERE `device_list`.id = %s;", (device_mode, id_device))
                    else:
                        print("Failed to insert data")
                else:
                    pass
            else:
                pass
    else:
        pass
# Describe get_list_device_in_process 
# 	 * @description get_list_device_in_process
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {mqtt_result }
# 	 * @return device_list 
# 	 */ 
async def get_list_device_in_process(mqtt_result):
    # Global variables
    global total_wmax_man,total_wmax,device_list
    
    # Local variable
    device_list = []
    wmax_array = []
    wmax = 0.0
    # Get result mqtt 
    if mqtt_result and isinstance(mqtt_result, list):
        for item in mqtt_result:
            # get info about device
            if 'id_device' in item and 'mode' in item and 'status_device' in item:
                id_device = item['id_device']
                mode = item['mode']
                results_device_type = item['name_device_type']
                # check device is inv
                if results_device_type == "PV System Inverter":
                    # get info list device
                    wmax_array = [field["value"] for param in item.get("parameters", []) if param["name"] == "Basic" for field in param.get("fields", []) if field["point_key"] == "WMax"]
                    wmax = wmax_array[0] if wmax_array else 0
                    
                    device_list.append({
                            'id_device': id_device,
                            'mode': mode,
                            'wmax': wmax,
                        })
# Describe process_sud_control_auto_man
# /**
# 	 * @description process_sud_control_auto_man
# 	 * @author bnguyen
# 	 * @since 17-06-2024
# 	 * @param {mqtt_result,serial_number_project,host, port, username, password}
# 	 * @return MySQL_Insert (device_mode, id_device)
# 	 */
async def process_sud_control_man(mqtt_result, serial_number_project, host, port, username, password):
    global arr
    global MQTT_TOPIC_PUB_CONTROL
    global device_mode
    global result_topic1
    global rated_power
    global rated_power_custom
    global rated_power_custom_calculator
    global rated_reactive_custom
    global power_limit_percent
    global power_limit_percent_enable
    global reactive_limit_percent
    global reactive_limit_percent_enable
    global emergency_stop
    global total_wmax_man 
    global value_power_limit
    global device_list
    global ModeSysTemp
    global ModeSysTemp_Control
    global value_offset_zero_export
    global bitcheck_topic1

    topicPublic = f"{serial_number_project}{MQTT_TOPIC_PUB_CONTROL}"
    id_systemp = int(arr[1])
    custom_watt = 0
    watt = 0
    comment = 200
    current_time = ""
    power_limit = 0
    value_zero_export = 0
    reactive_power_limit = 0
    total_wmax_man_temp = 0
    control_inv = 1
    result_value_power_limit = []
    if mqtt_result and any(int(item.get('id_device')) == int(id_systemp) for item in mqtt_result):
        result_topic1 = mqtt_result
        if result_topic1:
            bitcheck_topic1 = 1
            # Check Wmax with Value Maximum Power
            result_value_power_limit = MySQL_Select('SELECT value_power_limit,value_offset_power_limit,mode,control_mode,value_offset_zero_export FROM `project_setup`', ())
            value_power_limit_temp = result_value_power_limit[0]['value_power_limit']
            value_offset_power_limit = result_value_power_limit[0]['value_offset_power_limit']
            ModeSysTemp = result_value_power_limit[0]['mode']
            ModeSysTemp_Control = result_value_power_limit[0]['control_mode']
            value_offset_zero_export = result_value_power_limit[0]['value_offset_zero_export']
            
            if value_offset_zero_export :
                value_zero_export = value_zero_export_temp*(value_offset_zero_export/100)
            else:
                value_zero_export = value_zero_export_temp
            
            if value_offset_power_limit :
                value_power_limit = value_power_limit_temp*(value_offset_power_limit/100)
            else:
                value_power_limit = value_power_limit_temp
            
            if "rated_power_custom" not in result_topic1 and not any('status' in item for item in result_topic1):
                await process_update_mode_for_device(result_topic1, serial_number_project, host, port, username, password)
            else:
                pass

            for item in result_topic1:
                if int(item["id_device"]) == id_systemp and "rated_power_custom" in item and "rated_power" in item:
                    custom_watt = item.get("rated_power_custom", 0)
                    watt = item.get("rated_power", 0)
                    emergency_stop = item.get("emc", 0)
                    if custom_watt is None:
                        rated_power_custom_calculator = watt
                    else:
                        rated_power_custom_calculator = custom_watt

                    if emergency_stop != 1 :
                        for param in item.get("parameter", []):
                            if param["id_pointkey"] == "WMaxPercentEnable":
                                power_limit_percent_enable = param["value"]
                            elif param["id_pointkey"] == "WMax":
                                power_limit = param["value"]
                                # update power_limit Latest in device_list
                                for device in device_list:
                                    if device["id_device"] == id_systemp:
                                        device["wmax"] = power_limit
                                        device["mode"] = device_mode
                                        break

                                for device in device_list:
                                    if device["wmax"] is not None:
                                        if device["mode"] == 0:
                                            total_wmax_man_temp += device["wmax"]
                                    else:
                                        device["wmax"] = 0
                                # check wmax smaller rated power action . 
                                if (device_mode == 0 and power_limit < watt) or (device_mode == 1 and watt):
                                    rated_power = watt
                                    rated_power_custom = custom_watt
                                    
                            elif param["id_pointkey"] == "WMaxPercent":
                                power_limit_percent = power_limit_percent_enable and param["value"] or int((power_limit / rated_power_custom_calculator) * 100)
                            elif param["id_pointkey"] == "VarMaxPercentEnable":
                                reactive_limit_percent_enable = param["value"]
                            elif param["id_pointkey"] == "VarMax":
                                reactive_power_limit = param["value"]
                            elif param["id_pointkey"] == "VarMaxPercent":
                                if rated_reactive_custom is not None:
                                    reactive_limit_percent = reactive_limit_percent_enable and param["value"] or int((reactive_power_limit / rated_reactive_custom) * 100)
                                else:
                                    reactive_limit_percent = 0
                                    rated_reactive_custom = 0
                            
                        if power_limit_percent_enable:
                            item["parameter"] = [p for p in item["parameter"] if p["id_pointkey"] not in ["WMaxPercentEnable", "WMax", "WMaxPercent"]]
                        if reactive_limit_percent_enable:
                            item["parameter"] = [p for p in item["parameter"] if p["id_pointkey"] not in ["VarMaxPercentEnable", "VarMax", "VarMaxPercent"]]

                        # Check wmax with rated power  
                        if (power_limit > rated_power_custom_calculator) or \
                        (ModeSysTemp_Control == 2 and total_wmax_man > value_power_limit) or \
                        (ModeSysTemp_Control == 1 and total_wmax_man > value_zero_export):
                            item["parameter"] = [p for p in item["parameter"] if p["id_pointkey"] not in ["WMaxPercentEnable", "WMax", "WMaxPercent","PFSetEnable","PFSet","VarMaxPercentEnable", "VarMax", "VarMaxPercent"]]
                            comment = 400 
                            # If there is an error, there is no need to write it to inv anymore
                            data_send = {
                                    "time_stamp": current_time,
                                    "status": comment,
                                }
                            mqtt_public_paho_zip(host, port, topicPublic + "/Feedback", username, password, data_send)
                            result_topic1 = []
                        else:
                            comment = 200 
                            # check wmax smaller rated power action . 
                            if (device_mode == 0 and power_limit < watt) or (device_mode == 1 and watt):
                                rated_power = watt
                                rated_power_custom = custom_watt
                            MySQL_Update_V1('update `device_list` set `rated_power_custom` = %s, `rated_power` = %s where `id` = %s', (custom_watt, watt, id_systemp))
                            MySQL_Update_V1("UPDATE device_point_list_map dplm JOIN point_list pl ON dplm.id_point_list = pl.id SET dplm.control_max = %s WHERE pl.id_pointkey = 'Wmax' AND dplm.id_device_list = %s", (rated_power_custom_calculator, id_systemp))
                            custom_watt = 0
                            watt = 0
                        print("rated_power",rated_power)
                        print("custom_watt",custom_watt)
                        print("rated_power_custom",rated_power_custom)
                else:
                    if "parameter" in item and int(item["id_device"]) == id_systemp:
                        for param in item["parameter"]:
                            if param["id_pointkey"] == "ControlINV":
                                control_inv = param["value"]
                                if not control_inv:
                                    if "parameter" not in item:
                                        item["parameter"] = []
                                    item["parameter"].append({"id_pointkey": "Conn_RvrtTms", "value": 0})
                                    control_inv = True
                
# Describe process_message 
# 	 * @description processmessage from mqtt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {topic, message,serial_number_project, host, port, username, password}
# 	 * @return each topic , each message
# 	 */ 
async def process_message(topic, message,serial_number_project, host, port, username, password):
    global MQTT_TOPIC_SUD_CONTROL_MAN
    global MQTT_TOPIC_SUD_MODE_SYSTEMP
    global MQTT_TOPIC_SUD_CONTROL_AUTO
    global MQTT_TOPIC_SUD_DEVICES_ALL
    global MQTT_TOPIC_SUD_COMSUMTION_METER
    global device_mode 
    global mode_each_device
    global result_topic2
    global value_zero_export_temp
    global bitcheck_topic1

    topic1 = serial_number_project + MQTT_TOPIC_SUD_CONTROL_MAN
    topic2 = serial_number_project + MQTT_TOPIC_SUD_MODE_SYSTEMP
    topic3 = serial_number_project + MQTT_TOPIC_SUD_CONTROL_AUTO
    topic4 = serial_number_project + MQTT_TOPIC_SUD_DEVICES_ALL
    topic5 = serial_number_project + MQTT_TOPIC_SUD_COMSUMTION_METER
    
    result_topic1_Temp = []
    result_topic2 = ""
    result_topic4 = ""
    result_topic5 = ""
    try:
        if topic in [topic1, topic3]:
            result_topic1_Temp = message
            bitcheck_topic1 = 1
            await process_sud_control_man(result_topic1_Temp,serial_number_project, host, port, username, password)
        elif topic == topic2:
            result_topic2 = message
            # process 
            if result_topic2 and 'confirm_mode' in result_topic2:
                if result_topic2['confirm_mode'] in [0, 1]:
                    device_mode = result_topic2['confirm_mode']
                    mode_each_device = device_mode
                else:
                    pass
            else:
                pass
        elif topic == topic4:
            result_topic4 = message
            await get_list_device_in_process(result_topic4)
        elif topic == topic5:
            result_topic5 = message
            value_zero_export_temp = result_topic5["instant"]["consumption"]
    except Exception as err:
        print(f"Error process_message: '{err}'")
        
# Describe gzip_decompress 
# 	 * @description gzip_decompress
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {message}
# 	 * @return result_list
# 	 */ 
import base64
import gzip

def gzip_decompress(message):
    try:
        result_decode=base64.b64decode(message.decode('ascii'))
        result_decompress=gzip.decompress(result_decode)
        return json.loads(result_decompress)
    except Exception as err:
        print(f"decompress: '{err}'")
        
# Describe handle_messages_driver 
# 	 * @description handle_messages_driver
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {client, serial_number_project, topic1, topic2, topic3, host, port, username, password}
# 	 * @return all topic , all message
# 	 */ 
async def handle_messages_driver(client,serial_number_project, host, port, username, password):
    try:
        while True:
            message = await client.messages.get()
            if message is None:
                print('Broker connection lost!')
                break
            topic = message.topic
            payload = gzip_decompress(message.message)
            await process_message(topic, payload, serial_number_project, host, port, username, password)
    except Exception as err:
        print(f"Error handle_messages_driver: '{err}'")
# Describe sub_mqtt 
# 	 * @description sub_mqtt
# 	 * @author bnguyen
# 	 * @since 2-05-2024
# 	 * @param {}
# 	 * @return all topic , all message
# 	 */ 
async def sub_mqtt(host, port, username, password, serial_number_project, topic1, topic2, topic3,topic4,topic5):
    topics = [serial_number_project + topic1, serial_number_project + topic2, serial_number_project +topic3,serial_number_project +topic4,serial_number_project +topic5]
    try:
        client = mqttools.Client(
            host=host,
            port=port,
            username=username,
            password=bytes(password, 'utf-8'),
            subscriptions=topics,
            connect_delays=[1, 2, 4, 8]
        )
        
        while True:
            await client.start()
            await handle_messages_driver(client, serial_number_project,host, port, username, password)
            await client.stop()
    except Exception as err:
        print(f"Error MQTT sub_mqtt: '{err}'")

async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    if results_project != None :
        results_point_list_type= MySQL_Select('select * from `point_list_type`', ())
        serial_number_project=results_project[0]["serial_number"]
        tasks.append(asyncio.create_task(device(serial_number_project ,arr,
                                                        MQTT_BROKER,
                                                        MQTT_PORT,
                                                        MQTT_TOPIC_PUB_CONTROL,
                                                        MQTT_USERNAME,
                                                        MQTT_PASSWORD )))
        # 
        MQTT_BROKER_CLOUD=results_project[0]["mqtt_broker_cloud"] #"mqtt.nextwavemonitoring.com"
        MQTT_PORT_CLOUD=results_project[0]["mqtt_port_cloud"] #1883
        MQTT_USERNAME_CLOUD=results_project[0]["mqtt_username_cloud"] #"admin"
        MQTT_PASSWORD_CLOUD=results_project[0]["mqtt_password_cloud"] #"123654789"
        # 
        MQTT_BROKER_LIST=[]
        MQTT_PORT_LIST=[]
        MQTT_USERNAME_LIST=[]
        MQTT_PASSWORD_LIST=[]
        
        MQTT_BROKER_LIST.append(MQTT_BROKER)
        MQTT_PORT_LIST.append(MQTT_PORT)
        MQTT_USERNAME_LIST.append(MQTT_USERNAME)
        MQTT_PASSWORD_LIST.append(MQTT_PASSWORD)
        
        MQTT_BROKER_LIST.append(MQTT_BROKER_CLOUD)
        MQTT_PORT_LIST.append(MQTT_PORT_CLOUD)
        MQTT_USERNAME_LIST.append(MQTT_USERNAME_CLOUD)
        MQTT_PASSWORD_LIST.append(MQTT_PASSWORD_CLOUD)
        # 
        tasks.append(asyncio.create_task(monitoring_device(results_point_list_type,
                                                            serial_number_project,
                                                            MQTT_BROKER_LIST,
                                                            MQTT_PORT_LIST,
                                                            MQTT_USERNAME_LIST,
                                                            MQTT_PASSWORD_LIST
                                                            )))
        tasks.append(asyncio.create_task(sub_mqtt(
                                                MQTT_BROKER,
                                                MQTT_PORT,
                                                MQTT_USERNAME,
                                                MQTT_PASSWORD,
                                                serial_number_project,
                                                MQTT_TOPIC_SUD_CONTROL_MAN,
                                                MQTT_TOPIC_SUD_MODE_SYSTEMP,
                                                MQTT_TOPIC_SUD_CONTROL_AUTO,
                                                MQTT_TOPIC_SUD_DEVICES_ALL,
                                                MQTT_TOPIC_SUD_COMSUMTION_METER,
                                                )))
        
        await asyncio.gather(*tasks, return_exceptions=False)
    else:
        pass
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())