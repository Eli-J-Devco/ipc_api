

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
from pprint import pprint

import asyncio_mqtt as aiomqtt
import paho.mqtt.publish as publish

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import mqttools
import mybatis_mapper2sql
# import paho.mqtt.publish as publish
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
from configs.config import Config
from utils.libMySQL import *

arr = sys.argv
print(f'arr: {arr}')
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC|device_id|device_name
# Subscribe -> IPC|device_id|device_name|control
MQTT_TOPIC = Config.MQTT_TOPIC+"/Dev/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
query_device_rs485=""
all_device_data=[]
def getUTC():
    now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return now
def func_check_data_mybatis(data,item,object_name):
    try:
        
        if data[item].get(object_name):
           return data[item].get(object_name)
        else:
            return ""
        
    except Exception as err:
      print('Error not find object mybatis')
      return ""
# Describe functions before writing code
# /**
# 	 * @description Definition of point data
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {}
# 	 * @return data {ItemID, Name, Units, Value, Timestamp,Quality}
# 	 */
def point_object(Config,IDPoint,Parent,
                 ItemID,PointKey,
                 Name,Units,Value,Quality,Timestamp=None,
                 MsgError="", PointType=""):
    
    return {"Config":Config,
            "IDPoint":IDPoint,
            "Parent":Parent,
            "ItemID": ItemID,
            "PointKey":PointKey,
            "Name": Name, 
            "Units": Units, 
            "Value":  Value, 
            "Timestamp":(lambda x:  getUTC() if x ==None else x) (Timestamp),
            "Quality":Quality,
            "MsgError":MsgError,
            "PointType":PointType
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
    # except ModbusException as err:
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
        # print(f'data_of_register: {data_of_register}')
        # print(f'point_list_item: {point_list_item}')
        match point_list_item['pointtype']:
            case "Modbus register":
                match point_list_item['value_datatype']:
                    case 3: # Short Signed 16-bit
                        result = []
                        point_value :int = None
                        for itemD in data_of_register:
                            if point_list_item['register'] == itemD["MRA"]:
                                result.append(itemD["Value"])
                        # print(f'result: --- {result}')        
                        if len(result) > 0:
                            
                            decoder = BinaryPayloadDecoder.fromRegisters(
                                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                            point_value = decoder.decode_16bit_int()
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                                    point_list_item['id_point'],
                                                    point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'],
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'],
                                                    point_list_item['pointkey'],  
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                            
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'],
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    func_check_float(point_value), 
                                                    0)
                            
                            return point_list 
                        else:  
                            return point_list
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
                        else:
                            point_list=point_object(point_list_item['config_information'],
                                                    point_list_item['id_point'],
                                                    point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_value, 
                                                    1,
                                                    MsgError="Not found register"
                                                    )      
                        if point_value != None:
                            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                            point_list=point_object(point_list_item['config_information'],
                                                    point_list_item['id_point'],
                                                    point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    round(point_value,2), 
                                                    0)
                            
                            return point_list 
                        else:
                            return point_list 
                    case 10: # Double 64-bit real value
                        return {}
                    case _:
                        return {}
            case "Internal":
                point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    None, 
                                                    0,
                                                    )
                return point_list
            case "Equation":
                point_list=point_object(point_list_item['config_information'],
                                        point_list_item['id_point'],
                                        point_list_item['parent'],
                                                    # point_list_item['id_pointkey'], 
                                                    point_list_item['id'], 
                                                    point_list_item['pointkey'], 
                                                    point_list_item['unit_desc'], 
                                                    point_list_item['name_units'], 
                                                    point_list_item['constants'], 
                                                    0)
                return point_list
            # return point_list   
    except Exception as err:
        print(f'Error convert_register_to_point_list {err}')
        return {}
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
# Describe functions before writing code
# /**
# 	 * @description read modbus TCP
# 	 * @author vnguyen
# 	 * @since 20-11-2023
# 	 * @param {id_device, path (source run file python)}
# 	 * @return data ()
# 	 */ 
async def device(ConfigPara):
    try:
        # print(f'path: {path}')
        if len(ConfigPara)>=2 and type(ConfigPara) == list :
            pass
        else:
            return -1
        global query_device_rs485
        pathSource=path#ConfigPara[2]
        id_communication=ConfigPara[1]
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
        xml=pathSource + '/mybatis/device_list.xml')
        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True) 
        query_device_rs485= func_check_data_mybatis(statement,6,"select_all_device_rs485")
        query_point_list=func_check_data_mybatis(statement,2,"select_point_list")
        query_register_block=func_check_data_mybatis(statement,3,"select_register_block")
        
        if query_device_rs485 != -1 and query_point_list  != -1  and query_register_block  != -1:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        results_device = MySQL_Select(query_device_rs485, (id_communication,))
        # 
        if type(results_device) == list and len(results_device)>=1:
            pass
        else:           
            print("Error not found data device")
            return -1
        print(f'------ RS485 ----- ')
        serialport_group=results_device[0]["serialport_group"]
        serialport_name=results_device[0]["serialport_name"]
        serialport_baud=int(results_device[0]["serialport_baud"])
        serialport_stopbits=int(results_device[0]["serialport_stopbits"])
        serialport_parity=results_device[0]["serialport_parity"][0]
        serialport_timeout=int(results_device[0]["serialport_timeout"])
        # print(f'serialport_group: {serialport_group}')
        # print(f'serialport_name: {serialport_name}')
        # print(f'serialport_baud: {serialport_baud}')
        # print(f'serialport_stopbits: {serialport_stopbits}')
        # print(f'serialport_parity: {serialport_parity}')
        # print(f'serialport_timeout: {serialport_timeout}')
        # 
        
        # print(f'----- results_device -----')
        # for item in results_device:
        #     print(item)
        # print(f'----- +++++++++++++++++++++++++++++++++ -----')
        
        # all_device_data_request=[
        #     {
        #         "ID":1,
        #         "NAME":"INV1",
        #         "RB":[],
        #         "POINT":[]
        #     },
        #     {
        #         "ID":2,
        #         "NAME":"INV2",
        #         "RB":[],
        #         "POINT":[]
        #     }
        # ]
        all_device_data_request=[]
        for item in results_device:
            data_of_one_device={}
            data_of_one_device["ID"]=item['id']
            data_of_one_device["NAME"]=item['name']
            data_of_one_device["RB"]=[]
            data_of_one_device["POINT"]=[]
            # Register block
            item_rb= MySQL_Select(query_register_block, (item['id'],))
            new_item_rb=[]
            if type(item_rb) == list and len(item_rb)>=1:
                for new_item in item_rb:
                    new_item["rtu_bus_address"] =item["rtu_bus_address"]               
                    new_item_rb.append(new_item)
            if type(new_item_rb) == list and len(new_item_rb)>=1:
                data_of_one_device["RB"]=new_item_rb
         
                
            # Point list
            item_point= MySQL_Select(query_point_list, (item['id'],))
            if type(item_point) == list and len(item_point)>=1:
                data_of_one_device["POINT"]=item_point
            # 
            all_device_data_request.append(data_of_one_device)
        
            
       
        # for item in all_device_data_request:
        #     pprint(item, sort_dicts=False)
            
            
            
       
        while True:
            try:
                global all_device_data
                all_device_data=[]
                # 
                client = ModbusSerialClient(method="rtu", port=serialport_group, 
                                            stopbits=serialport_stopbits, 
                                            bytesize=8, 
                                            parity=serialport_parity, 
                                            baudrate=serialport_baud,
                                            strict=False)
                connection = client.connect()
                # all_device_data=[
                #     {   "ID":1,
                #         "NAME":"Device1",
                #         "MSG_DEVICE": "",
                #         "STATUS_REGISTER":[],
                #         "STATUS_DEVICE":""
                #         "POINT_LIST":[
                #                 {"tag1":1},
                #                 {"tag2":1},
                #                 {"tag3":1},
                #                 {"tag4":1}
                #                 ]},
                #     {   "ID":2,
                #         "NAME":"Device2",
                #         "MSG_DEVICE": "",
                #         "STATUS_REGISTER":[],
                #         "STATUS_DEVICE":""
                #         "POINT_LIST":[
                #                 {"tag1":1},
                #                 {"tag2":1},
                #                 {"tag3":1},
                #                 {"tag4":1}
                #                 ]}
                #     ]
      
                if connection:    
                    print(f'----- Get register -----')
                  
                    for item_device in all_device_data_request:
                        data_one_device={}
                        data_one_device["ID"]=item_device["ID"]
                        data_one_device["NAME"]=item_device["NAME"]
                        data_one_device["MSG_DEVICE"]=""
                        data_one_device["STATUS_REGISTER"]=[]
                        data_one_device["POINT_LIST"]=[]
                        data_one_device["STATUS_DEVICE"]=""
                        
                        data_rg_one_device = []
                        status_rb=[]
                        status_device=""
                        # Read register block 1 device
                        for itemRB in item_device["RB"]:
                            device_name_rs485=itemRB["name"]
                            slave_ip=itemRB["rtu_bus_address"]
                            await asyncio.sleep(0.5)
                            FUNCTION = itemRB["Functions"]
                            ADDR = itemRB["addr"]
                            COUNT = itemRB["count"]
                            # print('----------- itemRB ---------------------')
                            # pprint(f'{itemRB}', sort_dicts=False)
                            result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ip)
                            try:                                  
                                if result_rb==[]:
                                        print("The device does not return results")
                                else:
                                    if not result_rb.isError():
                                        status_device="ONLINE"
                                        INC = ADDR-1
                                        for itemR in result_rb.registers:
                                            INC = INC+1
                                            data_rg_one_device.append({"MRA": INC, "Value": itemR, })
                                    else:
                                        print("Error ------------------------------------")
                                        # print(f"Error reading from {slave_ip} : {result_rb}")
                                        status_device="ONLINE"
                                        print(f'Name: {device_name_rs485 } ADDR: {ADDR} COUNT: {COUNT} ')
                                        if hasattr(result_rb, 'function_code'):
                                            print(f'ERROR CODE: {result_rb.function_code}')
                                            status_rb.append({"ADDR":ADDR,
                                                              "ERROR_CODE":result_rb.function_code,
                                                               "Timestamp": getUTC(),
                                                              })
                                        else:
                                            print(f'This Slave {device_name_rs485} - [{slave_ip}] was not found')
                                            status_device="OFFLINE"
                                            status_rb.append({"ADDR":ADDR,
                                                              "ERROR_CODE":139,
                                                               "Timestamp": getUTC(),
                                                              })                                 
                            except AttributeError as ae:
                              print('An exception occurred',ae)
                              
                        new_Data = [x for i, x in enumerate(data_rg_one_device) if x['MRA'] not in {y['MRA'] for y in data_rg_one_device[:i]}]
                        # print(f'----- Value new_Data -----')
                        # pprint(new_Data, sort_dicts=False)
                        
                        # Read point list 1 device
                        data_point_list_one_device = []
                        for itemP in item_device["POINT"]:
                            result= convert_register_to_point_list(itemP,new_Data)
                            if len(result)>0:
                                data_point_list_one_device.append(result)
                            else:
                                pass
                        data_one_device["STATUS_REGISTER"]=status_rb
                        data_one_device["POINT_LIST"]=data_point_list_one_device
                        data_one_device["STATUS_DEVICE"]=status_device
                        all_device_data.append(data_one_device)
                else:
                    print(f'----- Can not connect to port -----')
                    for item_device in all_device_data_request:
                        data_one_device={}
                        data_one_device["ID"]=item_device["ID"]
                        data_one_device["NAME"]=item_device["NAME"]
                        data_one_device["MSG_DEVICE"]="Can't connect to modbus RTU"
                        data_one_device["STATUS_REGISTER"]=[]
                        data_one_device["POINT_LIST"]=[]
                        data_one_device["STATUS_DEVICE"]="OFFLINE"
                        all_device_data.append(data_one_device)
                        
                client.close()
                await asyncio.sleep(2)
            except (ConnectionException, ModbusException) as e:
                print(f"Modbus error from: {e}")
                await asyncio.sleep(5)
            except AttributeError as ae:
                print("AE ERROR", ae)
                await asyncio.sleep(5)

    # except ConnectionException as ce:
    #     print("CE ERROR")
    # except AttributeError as ae:
    #     print(f"Modbus error from : {ae}")
    except Exception as err:
        
        print('Error device : ',err)
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 20-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(serial_number_project,host, port,topic, username, password
                       
                       ):
    try:
        while True:
            print(f'-----{getUTC()} monitoring_device -----')
            global all_device_data
            # pprint(all_device_data, sort_dicts=False)
            # global  device_name,status_Device,msg_device,status_register_block,point_list_device
          
          
            for item in all_device_data:
                device_id=str(item['ID'])
                device_name=str(item['NAME'])
                data_mqtt={
                "ID_DEVICE":device_id,
                "STATUS_DEVICE":item['STATUS_DEVICE'],
                "TIME_STAMP":getUTC(),
                "MSG_DEVICE":item['MSG_DEVICE'],
                "STATUS_REGISTER":item['STATUS_REGISTER'],
                "POINT_LIST":item['POINT_LIST'],
                            }
                # func_mqtt_public(   host,
                #                     port,
                #                     topic+""+device_id+"|"+device_name,
                #                     username,
                #                     password,
                #                     data_mqtt)
                func_mqtt_public(   host,
                                    port,
                                    serial_number_project+"/"+"Devices/"+""+device_id,
                                    username,
                                    password,
                                    data_mqtt)
            await asyncio.sleep(2)
        
    except Exception as err:
        print('Error monitoring_device : ',err)
async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    serial_number_project=results_project[0]["serial_number"]
    tasks.append(asyncio.create_task(device(arr)))
    tasks.append(asyncio.create_task(monitoring_device( serial_number_project,
                                                    MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC,
                                                    MQTT_USERNAME,
                                                    MQTT_PASSWORD
                                                                                        
                                                    )))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())