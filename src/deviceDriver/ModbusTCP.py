

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

import asyncio_mqtt as aiomqtt
# absDirname: D:\NEXTWAVE\project\ipc_api\driver_of_device
# absDirname=os.path.dirname(os.path.abspath(__file__))
import mqttools
import mybatis_mapper2sql
# import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
# from async_paho_mqtt_client import AsyncClient
# from asyncio_paho import AsyncioPahoClient
# from asyncio_paho.client import AsyncioMqttAuthError
# 
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

sys.stdout.reconfigure(encoding='utf-8')
# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
#                 ("src"))
path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMQTT import *
from utils.libMySQL import *
from utils.libTime import *

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
MQTT_TOPIC_PUD_MODECONTROL_DEVICE = "/Control/Setup/Mode/Write"
MQTT_TOPIC_SUD_CONFIRM_MODE_SYSTEMP = "/Control/Setup/Mode/Feedback"
MQTT_TOPIC_SUD_CONFIRM_MODE_DEVICE = "/Control/Write"
# 
ModeSysTemp = "" 
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


result_topic1 = ""
result_topic2 = ""
result_topic3 = ""
result_topic4 = ""

enable_zero_export = 0
value_zero_export = 0
enable_power_limit = 0
value_power_limit = 0

bitchecktopic1 = 0
bitchecktopic2 = 0
bitchecktopic3 = 0
bitchecktopic4 = 0
bitchecktopic5 = 0
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
                 ):
    
    return {"config":Config,
            "id_point_list_type":id_point_type,
            "name_point_list_type":name_point_type,
            "id_point":id_point,
            "parent":parent,
            "id": id,
            "point_key":point_key,
            "name": name, 
            "unit": unit, 
            "value":  value, 
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
            "control_enabled":control_enabled
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
                            if point_list_item['register'] == itemD["MRA"]:
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
                            if point_list_item['register'] == itemD["MRA"]:
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
                            Rn.append(R1)
                            Rn.append(R2)
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"]:
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
                            Rn.append(R1)
                            Rn.append(R2)
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"]:
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
                            
                            Rn.append(R1)
                            Rn.append(R2)
                            Rn.append(R3)
                            Rn.append(R4)
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"]:
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
                            
                            Rn.append(R1)
                            Rn.append(R2)
                            Rn.append(R3)
                            Rn.append(R4)
                        for item in Rn:
                            for itemD in data_of_register:
                                if item == itemD["MRA"]:
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
                            if point_list_item['register'] == itemD["MRA"]:
                                result.append(itemD["Value"])
                        for itemD in data_of_register:
                            if point_list_item['register']+1 == itemD["MRA"]:
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
                                                            control_enabled=1
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
                                                control_enabled=1
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
                                        control_enabled=1
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
                                        control_enabled=1
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
# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# path=""
# from database import get_db
# from libcom import func_mqtt_public_alarm
# from models import Alarm, Device_list, Error, Project_setup, Screen

# db=get_db()
async def check_inverter_device(device_control):
    results_device_type = []
    
    query = "SELECT `device_type`.`name` FROM device_type INNER JOIN `device_list` ON device_list.id_device_type=device_type.id WHERE device_list.id=%s;"
    results_device_type = MySQL_Select(query, (device_control,))
    if results_device_type and results_device_type[0]["name"] == "PV System Inverter":
        return True  
    else:
        return False  

async def find_inverter_information(device_control , parameter):
    results_register = []
    results_datatype = []
    inverter_information = []
    inverter_information_full = []
    query_register = "SELECT point_list.id_pointkey , point_list.`register`, point_list.id_type_datatype FROM `point_list` INNER JOIN `device_list` ON device_list.id_template = point_list.id_template WHERE device_list.id = %s;"
    query_datatype = "SELECT `config_information`.`value` FROM `config_information` WHERE `config_information`.id = %s"
    
    results_register = MySQL_Select(query_register, (device_control,))
    
    if results_register :
        inverter_information = [item for item in results_register if item['id_pointkey'] in [p['id_pointkey'] for p in parameter]]
        
        # Iterate through the new list to assign values from the corresponding variables
        for item in inverter_information:
            for p in parameter:
                if item['id_pointkey'] == p['id_pointkey']:
                    item['value'] = p['value']
    
    for item in inverter_information:
        value = item["value"]
        register = item["register"]
        type_datatype = item["id_type_datatype"]
        id_pointkey = item['id_pointkey']

        # Tìm kiếm datatype tương ứng
        results_datatype = MySQL_Select(query_datatype, (type_datatype,))
        if results_datatype:
            datatype = results_datatype[0]["value"]
        else:
            datatype = None  # Xử lý trường hợp không tìm thấy datatype

        # Thêm biến datatype vào phần tử và thêm vào danh sách mới
        item_with_datatype = {
            "value": value,
            "register": register,
            "id_type_datatype": type_datatype,
            "id_pointkey": id_pointkey,
            "datatype": datatype
        }
        inverter_information_full.append(item_with_datatype)
        
    return inverter_information_full
    
async def write_device(ConfigPara ,client ,slave_ID , serial_number_project , mqtt_host, mqtt_port, topicPublic, mqtt_username, mqtt_password):
    
    topicPublic = serial_number_project + topicPublic
    id_systemp = ConfigPara[1]
    id_systemp = int(id_systemp)
    pathSource=path
    
    global device_mode
    global status_device
    
    # Man (device_mode == 0 ) + result_topic1 + bitchecktopic1 == 1 + enable_zero_export == 0 : 
    global result_topic1
    global bitchecktopic1
    result_temp = []
    result_temp = result_topic1
    
    if result_temp and bitchecktopic1 == 1 :
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
        xml=pathSource + '/mybatis/device_list.xml')
        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True) 
        QUERY_INFORMATION_CONNECT_MODBUS_TCP = func_check_data_mybatis(statement,9,"QUERY_INFORMATION_CONNECT_MODBUSTCP")
        QUERY_TYPE_DEVICE = func_check_data_mybatis(statement,11,"QUERY_TYPE_DEVICE")
        QUERY_REGISTER_DATATYPE = func_check_data_mybatis(statement,12,"QUERY_REGISTER_DATATYPE")
        QUERY_DATATYPE = func_check_data_mybatis(statement,13,"QUERY_DATATYPE")
        # query_device_control=func_check_data_mybatis(statement,4,"select_device_control")
        if QUERY_TYPE_DEVICE != -1 and QUERY_INFORMATION_CONNECT_MODBUS_TCP != -1 and QUERY_ALL_DEVICES != -1 and QUERY_REGISTER_DATATYPE != -1 and QUERY_DATATYPE:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        for item in result_temp:
            device_control = item['id_device']
            parameter = item['parameter']
            
            if id_systemp == device_control :
                if parameter :
                    print("---------- write data from Device ----------")
                    try:
                        # result Modbus
                        results_write_modbus = []
                        
                        # information Modbus 
                        register = ""
                        datatype = ""
                        code_value = 0
                        id_pointkey = ""
                        
                        #mqtt
                        comment = 200
                        current_time = get_utc()
                        data_send = ""
                        
                        # database
                        is_inverter = []
                        inverter_info = []
                        result_query_findname = []
                        name_device_points_list_map = ""
                        
                        if device_control :
                            is_inverter = await check_inverter_device(device_control)
                        else :
                            pass

                        # if device is INV 
                        if is_inverter:
                            inverter_info = await find_inverter_information(device_control, parameter)

                            for item in inverter_info:
                                value = item["value"]
                                register = item["register"]
                                id_pointkey = item['id_pointkey']
                                datatype = item["datatype"]
                                
                                # Find 'name' in device_point_list_map
                                result_query_findname = MySQL_Select('select `name` from `point_list` where `register` = %s and `id_pointkey` = %s', (register,id_pointkey,))
                                name_device_points_list_map = result_query_findname [0]["name"]
                                
                                try:
                                    if device_mode == 0 :
                                        print("---------- Manual control mode ----------")
                                        if len(inverter_info) == 1 and parameter[0]['id_pointkey'] == "ControlINV":
                                            if value == True :
                                                results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, register, value=1)
                                                MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(1,device_control,name_device_points_list_map))
                                            elif value == False :
                                                results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, register, value=0)
                                                MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(0,device_control,name_device_points_list_map))
                                            # get status INV 
                                            if results_write_modbus:
                                                code_value = results_write_modbus['code']
                                                if code_value == 16 :
                                                    comment = 200
                                                elif code_value == 144 :
                                                    comment = 400

                                        if len(inverter_info) >= 1 and (isinstance(value, int) or isinstance(value, float)):
                                            results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, register, value=value)
                                            MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(value,device_control,name_device_points_list_map))
                                            # get status INV 
                                            if results_write_modbus:
                                                code_value = results_write_modbus['code']
                                                if code_value == 16 :
                                                    comment = 200
                                                elif code_value == 144 :
                                                    comment = 400
                                        # after control INV => Done pud status device to MQTT and resset Araay Sent data 
                                        data_send = {
                                            "time_stamp" :current_time,
                                            "status":comment, 
                                            }
                                        if bitchecktopic1 == 1 and code_value == 16 :
                                            push_data_to_mqtt(mqtt_host,
                                                    mqtt_port,
                                                    topicPublic + "/" +"Feedback" ,
                                                    mqtt_username,
                                                    mqtt_password,
                                                    data_send)
                                            # resset data
                                            bitchecktopic1 == 0
                                            result_topic1 = []
                                        else :
                                            pass
                                        
                                    if device_mode == 1 :
                                        print("---------- Auto control mode ----------")
                                        if len(inverter_info) >= 1 and parameter[0]['id_pointkey'] == "WMax":
                                            results_write_modbus = write_modbus_tcp(client, slave_ID, datatype, register, value=value)
                                            MySQL_Update_V1('update `device_point_list_map` set `output_values` = %s where `id_device_list` = %s AND `name` = %s',(value,device_control,name_device_points_list_map))
                                            # get status INV 
                                            if results_write_modbus:
                                                code_value = results_write_modbus['code']
                                                if code_value == 16 :
                                                    comment = 200
                                                elif code_value == 144 :
                                                    comment = 400
                                        # Feedback confirms the device has switched to auto mode
                                        data_send = {
                                            "time_stamp" :current_time,
                                            "status":comment, 
                                            }
                                        if bitchecktopic1 == 1 :
                                            push_data_to_mqtt(mqtt_host,
                                                    mqtt_port,
                                                    topicPublic + "/" +"Feedback" ,
                                                    mqtt_username,
                                                    mqtt_password,
                                                    data_send)
                                            bitchecktopic1 == 0
                                            result_topic1 = []
                                        else :
                                            pass
                                        
                                except Exception as e:
                                    print(f"An error occurred: {e}")
                        else :
                            pass
                            
                    except Exception as err:
                        print(f"Error MQTT subscribe: '{err}'")
                else:
                    pass
            else:
                pass
    
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
        pathSource=path
        print(f'pathSource: {pathSource}')
        # pathSource="D:/NEXTWAVE/project/ipc_api"
        id_device=ConfigPara[1]
        device_id = id_device
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
        xml=pathSource + '/mybatis/device_list.xml')
        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True) 
        # 
        query_all= func_check_data_mybatis(statement,0,"select_all_device")
        query_only_device=func_check_data_mybatis(statement,1,"select_only_device")
        query_point_list=func_check_data_mybatis(statement,2,"select_point_list")
        query_register_block=func_check_data_mybatis(statement,3,"select_register_block")
        # query_device_control=func_check_data_mybatis(statement,4,"select_device_control")
        if query_all != -1 and query_only_device  != -1 and query_point_list  != -1 and query_register_block  != -1:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        # 
        
        results_device = MySQL_Select(query_only_device, (id_device,))
        # print(results_device)
        # 
        if type(results_device) == list and len(results_device)>=1:
            pass
        else:           
            print("Error not found data device")
            return -1
        # print(f'results_device: {results_device}')
        id_template=results_device[0]["id_template"]
        # print(f'query_register_block: {query_register_block}')
        results_RBlock= MySQL_Select(query_register_block, (id_template,))
        results_Plist= MySQL_Select(query_point_list, (id_device,))
        # print(f'results_rblock: {results_RBlock[0]}')
        # print(f'results_plist: {results_Plist}')
        # Check the register Modbus
        if type(results_RBlock) == list and len(results_RBlock)>=1:
            pass
        else:           
            print("Error device register not found")
            # return -1
        # Check the point list Modbus
        if type(results_Plist) == list and len(results_Plist)>=1:
            pass
        else:           
            print("Error device point list not found")
            # return -1 
        # inv_shutdown_enable=results_device[0]["enable_poweroff"]
        device_mode=results_device[0]['mode']
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
                            await asyncio.sleep(0.5)
                            FUNCTION = itemRB["Functions"]
                            ADDR = itemRB["addr"]
                            COUNT = itemRB["count"]
                            result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ID)
                            if result_rb==[]:
                                print("The device does not return results")
                            else:
                                if not result_rb.isError():
                                    status_device="online"
                                    INC = ADDR-1
                                    for itemR in result_rb.registers:
                                        INC = INC+1
                                        Data.append({"MRA": INC, "Value": itemR, })
                                else:
                                    print("Error ------------------------------------")
                                    print(f'ADDR: {ADDR} COUNT: {COUNT}')
                                    if hasattr(result_rb, 'function_code'):
                                        status_device="online"
                                        # Exception Response(131, 3, IllegalAddress)
                                        print(f'ERROR CODE: {result_rb.function_code}')
                                        #
                                        print(f"Error reading from {slave_ip}: {result_rb}")
                                        status_rb.append({"ADDR":ADDR,
                                                        "ERROR_CODE":result_rb.function_code,
                                                        "Timestamp": getUTC(),
                                                        })
                                        status_register_block=status_rb
                                    else:
                                        print(f'This Slave {device_name} - [{slave_ip}] was not found')
                                        status_device="offline"
                                        status_rb.append({"ADDR":ADDR,
                                                              "ERROR_CODE":139,
                                                               "Timestamp": getUTC(),
                                                              })      
                        new_Data = [x for i, x in enumerate(Data) if x['MRA'] not in {y['MRA'] for y in Data[:i]}]
                        # print(f"Register Block {slave_ip}: {new_Data}")  
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
                                                ))
                    else:
                        # print(results_Plist[0])
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
                                                control_enabled=1
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
        print('Exception device : ', type(err).__name__)
        
        # raise Exception("Runtime Error!!!") 
    finally:
        print ("--Finally--")      
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
        results_control_group = MySQL_Select(f'SELECT * FROM point_list_control_group where id_template={id_template} and status=1', ())
        print(f'init monitoring_device')
        # point_list
        # 1: Number, 2: String, 3: Percent, 4: Bool
        # point_list_control_group
        # 0=Independent, 1=Depends one, 2=Depends two
        while True:
            print(f'-----{getUTC()} monitoring_device -----')
            global  device_name,status_device,msg_device,status_register_block,point_list_device
            global device_id
            global NAME_DEVICE_TYPE
            global ID_DEVICE_TYPE
            global device_mode
            new_point_list_device=[]
            new_point=[]
            mppt=[]
            control_group=[]
            match NAME_DEVICE_TYPE:
                case "PV System Inverter":
                    pass
                case "Solar Tracker":
                    pass
                case "Production Meter":
                    pass
                case "Weather Station":
                    pass
                case "Datalogger":
                    pass
                case "Sensor":
                    pass
                case "Load meter":
                    pass
                case "SMA Communication products":
                    pass
                case "Consumption meter":
                    pass
                case "Cell Modem":
                    pass
                case "Virtual Meter":
                    pass
                case "UPS":
                    pass
            #
            if results_control_group:
                control_group=[
                    {
                        "id":item["id"],
                        "name":item["name"],
                        "description":item["description"],
                        "attributes":item["attributes"],
                        "fields":[]
                        
                    } for item in results_control_group]
            for item in point_list_device:
                new_point_list_device.append({
                    **item,
                    "timestamp":getUTC()
                })
            # 
            if new_point_list_device:
                for point_item in new_point_list_device:
                    if point_item['config']=="MPPT":
                        mppt_strings=[]
                        mppt_volt=[]
                        mppt_amps=[]                 
                        mppt_volt=[item for item in new_point_list_device if item['parent'] == point_item["id_point"] and item['config'] =="MPPTVolt" ]
                        mppt_amps=[item for item in new_point_list_device if item['parent'] == point_item["id_point"]and item['config'] =="MPPTAmps"]
                        mppt_string=[item for item in new_point_list_device if item['parent'] == point_item["id_point"]and item['config'] =="StringAmps"]
                        for item in mppt_string:
                            mppt_strings.append({
                                "point_key":item["point_key"],
                                "name":item["name"],
                                "value":item["value"],
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
                        mppt_item={
                                "config":point_item["config"],
                                "id_point":point_item["id_point"],
                                "parent":point_item["parent"],
                                "id": point_item["id"],
                                "point_key":point_item["point_key"],
                                "name": point_item["name"],
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
                                # "config":item_point["config"],
                                # "id_point_list_type":item_point["id_point_list_type"],
                                # "name_point_list_type":item_point["name_point_list_type"],
                                # "id_point":item_point["id_point"],
                                # "parent":item_point["parent"],
                                # "id":item_point["id"],
                                # "point_key":item_point["point_key"],
                                # "name":item_point["name"],
                                # "unit":item_point["unit"],
                                # "value":item_point["value"],
                                # "timestamp":item_point["timestamp"],
                                # "quality":item_point["quality"],
                                # "message":item_point["message"],
                                # "point_type":item_point["point_type"],
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
                                        elif item_point_attr['control_menu_order'] == 2:
                                            new_point_control_attr.append(
                                                {
                                                    **item_point_attr,
                                                    "control_enabled":(lambda x: 1  if x==0 else 0)(control_enable)
                                                }
                                            )
                                        elif item_point_attr['control_menu_order'] == 3:
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
            # print(f'new_control_group: {new_control_group}')
            data_device={
                "id_device":device_id,
                "mode":device_mode,
                "device_name":device_name,
                "id_device_type":ID_DEVICE_TYPE,
                "name_device_type":NAME_DEVICE_TYPE,
                "status_device":status_device,
                "timestamp":getUTC(),
                "message":msg_device,
                "status_register":status_register_block,
                "point_count":len(new_point),
                "parameters":parameters,
                "fields":new_point,
                "mppt":mppt,
                "control_group":new_control_group
            }
            data_device_short={
                "id_device":device_id,
                "mode":device_mode,
                "device_name":device_name,
                "id_device_type":ID_DEVICE_TYPE,
                "name_device_type":NAME_DEVICE_TYPE,
                "status_device":status_device,
                "timestamp":getUTC(),
                "message":msg_device,
                "status_register":status_register_block,
                # "point_count":len(new_point),
                # "parameters":parameters,
                "fields":new_point,
                # "mppt":mppt,
                # "control_group":new_control_group
            }
            
            if device_name !="" and serial_number_project!= None:
                
                func_mqtt_public(   host[0],
                                    port[0],
                                    serial_number_project+"/"+"Devices/"+""+device_id,
                                    username[0],
                                    password[0],
                                    data_device)
                func_mqtt_public(   host[0],
                                    port[0],
                                    serial_number_project+"/"+"Shorts/"+""+device_id,
                                    username[0],
                                    password[0],
                                    data_device_short)
                # 
                if host[1] != None and port[1]:
                    func_mqtt_public(   host[1],
                                        port[1],
                                        serial_number_project+"/"+"Devices/"+""+device_id,
                                        username[1],
                                        password[1],
                                        data_device)
            
            await asyncio.sleep(1)
        
    except Exception as err:
        print('Error monitoring_device : ',err)
        
    #   return -1
# Describe functions before writing code
# /**
# 	 * @description mqtt subscribe
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
        
async def process_update_mode_for_device(mqtt_result,serial_number_project,host, port, username, password):
    global device_mode
    global status_device
    global arr 
    global MQTT_TOPIC_PUD_MODECONTROL_DEVICE
    
    topicpud = serial_number_project + MQTT_TOPIC_PUD_MODECONTROL_DEVICE
    id_device = 0
    id_systemp = arr[1]
    id_systemp = int(id_systemp)
    result_checkmode_control = []
    result_checktype_device = []
    checktype_device = ""
    
    try:
        if mqtt_result and all(item.get('id_device') != 'Systemp' for item in mqtt_result):
            for item in mqtt_result:
                id_device = int(item["id_device"])
                result_checktype_device = MySQL_Select ("SELECT device_type.name FROM device_list JOIN device_type ON device_list.id_device_type = device_type.id WHERE device_list.id = %s;" ,(id_device,) )
                checktype_device = result_checktype_device[0]["name"]
                if checktype_device == "PV System Inverter":
                    if id_device == id_systemp:
                        device_mode = int(item["mode"])

                        querydevice = "UPDATE device_list SET device_list.mode = %s WHERE `device_list`.id = %s;"
                        
                        if device_mode in [0, 1]:  
                            MySQL_Insert_v5(querydevice, (device_mode, id_device))  
                            result_checkmode_control = await MySQL_Select_v1("SELECT device_list.mode FROM device_list JOIN device_type ON device_list.id_device_type = device_type.id WHERE device_type.name = 'PV System Inverter';")

                            if any(item['mode'] for item in result_checkmode_control) and any(item['mode'] == 1 for item in result_checkmode_control):
                                data_send = {
                                            "id_device": "Systemp",
                                            "mode": 2
                                            }
                                push_data_to_mqtt(host,
                                        port,
                                        topicpud ,
                                        username,
                                        password,
                                        data_send)
                            elif all(item['mode'] == 0 for item in result_checkmode_control):
                                data_send = {
                                            "id_device": "Systemp",
                                            "mode": 0
                                            }
                                push_data_to_mqtt(host,
                                        port,
                                        topicpud ,
                                        username,
                                        password,
                                        data_send)
                            elif all(item['mode'] == 1 for item in result_checkmode_control):
                                data_send = {
                                            "id_device": "Systemp",
                                            "mode": 1
                                            }
                                push_data_to_mqtt(host,
                                        port,
                                        topicpud ,
                                        username,
                                        password,
                                        data_send)
                            else:
                                pass
                        else:
                            print("Failed to insert data")
                    else :
                        pass
                else:
                    pass
        else:
            pass
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")
        
async def sud_mqtt(serial_number_project, host, port, topic1, topic2, username, password):
    
    global result_topic1 
    global result_topic2 
    
    topic1 = serial_number_project + topic1
    topic2 = serial_number_project + topic2
    
    global bitchecktopic1 
    global bitchecktopic2
    
    # variable topic 1
    # variable topic 2
    global device_mode
    
    try:
        client = mqttools.Client(host=host, port=port, username=username, password=bytes(password, 'utf-8'))
        if not client:
            return -1 
        
        await client.start()
        await client.subscribe(topic1)
        await client.subscribe(topic2)
        
        while True:
            try:
                message = await asyncio.wait_for(client.messages.get(), timeout=5.0)
            except asyncio.TimeoutError:
                continue
            
            if not message:
                print("Not find message from MQTT")
                continue
            
            if message.topic == topic1:
                result_topic1 = json.loads(message.message.decode())
                #process
                if result_topic1 :
                    bitchecktopic1 = 1 
                    await process_update_mode_for_device(result_topic1,serial_number_project,host, port, username, password)
                
            elif message.topic == topic2:
                result_topic2 = json.loads(message.message.decode())
                # process 
                if result_topic2 and 'confirm_mode' in result_topic2:
                    if result_topic2['confirm_mode'] in [0, 1]:
                        device_mode = result_topic2['confirm_mode']
                    else:
                        pass
                else:
                    pass
                
    except Exception as err:
        print(f"Error MQTT subscribe: '{err}'")

async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
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
    tasks.append(asyncio.create_task(monitoring_device(results_point_list_type,serial_number_project,
                                                    MQTT_BROKER_LIST,
                                                    MQTT_PORT_LIST,
                                                    MQTT_USERNAME_LIST,
                                                    MQTT_PASSWORD_LIST
                                                    )))
    tasks.append(asyncio.create_task(sud_mqtt(serial_number_project,
                                                    MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC_SUD_CONFIRM_MODE_DEVICE,
                                                    MQTT_TOPIC_SUD_CONFIRM_MODE_SYSTEMP,
                                                    MQTT_USERNAME,
                                                    MQTT_PASSWORD
                                                    )))
    
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())