

# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/

import datetime
import json
import os
import sys
import time

import mybatis_mapper2sql
import paho.mqtt.publish as publish
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

# absDirname: D:\NEXTWAVE\project\ipc_api\driver_of_device
# absDirname=os.path.dirname(os.path.abspath(__file__))

sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from config import *
from libMySQL import *

arr = sys.argv
print(f'arr: {arr}')
# MQTT_BROKER = Config.MQTT_BROKER
MQTT_BROKER = 'test.mosquitto.org' #Demo
MQTT_PORT = Config.MQTT_PORT
MQTT_TOPIC = Config.MQTT_TOPIC
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD

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
def point_object(ItemID,Name,Units,Value,Quality):
    
    return {"ItemID": ItemID, 
            "Name": Name, 
            "Units": Units, 
            "Value":  Value, 
            "Timestamp": getUTC(),
            "Quality":Quality
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
    except:
      print('An exception occurred')
   
# Describe functions before writing code
# /**
# 	 * @description convert data of register to point list
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {point_list_item,data_of_register}
# 	 * @return data (ItemID, Name, Units, Value, Timestamp,Quality)
# 	 */

def convert_register_to_point_list(point_list_item,data_of_register):
    point_list=None
    if point_list_item['value_datatype'] == 3: # Short Signed 16-bit
        result = []
        point_value :int = None
        for itemD in data_of_register:
            if point_list_item['register'] == itemD["MRA"]:
                result.append(itemD["Value"])
        if len(result) > 0:
            decoder = BinaryPayloadDecoder.fromRegisters(
                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
            point_value = decoder.decode_16bit_int()
        else:
            point_list=point_object(point_list_item['id_pointkey'], 
                                    point_list_item['unit_desc'], 
                                    point_list_item['name_units'], 
                                    point_value, 
                                    1)
        if point_value != None:
            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
            point_list=point_object(point_list_item['id_pointkey'], 
                                    point_list_item['unit_desc'], 
                                    point_list_item['name_units'], 
                                    func_check_float(point_value), 
                                    0)
    if point_list_item['value_datatype'] == 4: # Word Unsigned 16-bit
        pass
    if point_list_item['value_datatype'] == 5: # Long Signed 32-bit
        pass
    if point_list_item['value_datatype'] == 6: # DWord Unsigned 32-bit
        pass
    if point_list_item['value_datatype'] == 7: # LLong Signed 64-bit
        pass
    if point_list_item['value_datatype'] == 8: # QWord Unsigned 64-bit 
            pass
    if point_list_item['value_datatype'] == 9: # Float 32-bit real value IEEE-754
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
            point_list=point_object(point_list_item['id_pointkey'], 
                                    point_list_item['unit_desc'], 
                                    point_list_item['name_units'], 
                                    point_value, 
                                    1)      
        if point_value != None:
            point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
            point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
            point_list=point_object(point_list_item['id_pointkey'], 
                                    point_list_item['unit_desc'], 
                                    point_list_item['name_units'], 
                                    round(point_value,2), 
                                    0)
    if point_list_item['value_datatype'] == 10: # Double 64-bit real value
            pass
    return point_list
def func_decoder_modbus():
    pass
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
        
    except:
      print('Error not find object mybatis')
      return ""
# ----- MQTT -----
# Describe functions before writing code
# /**
# 	 * @description public data MQTT
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {Broker, Port,Topic, UserName, Password, data_send}
# 	 * @return data ()
# 	 */
def func_mqtt_public(Broker, Port,Topic, UserName, Password, data_send):
    try:
        payload = json.dumps(data_send)
      
        # publish.single(Topic, payload, hostname=Broker,
        #                retain=False, port=Port,
        #                auth = {'username':f'{UserName}', 
        #                        'password':f'{Password}'})
        publish.single(Topic, payload, hostname=Broker,
                    retain=False, port=Port)
    except Error as err:
        print(f"MQTT Error: '{err}'")
# 
def device(ConfigPara):
    try:
        
        if len(ConfigPara)>=2 and type(ConfigPara) == list :
            pass
        else:
            return -1
        pathSource=ConfigPara[2]
        # pathSource="D:/NEXTWAVE/project/ipc_api"
        id_device=ConfigPara[1]
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
        xml=pathSource + '/mybatis/device_list.xml')
        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True) 
        # 
        query_all= func_check_data_mybatis(statement,0,"select_all_device")
        query_only_device=func_check_data_mybatis(statement,1,"select_only_device")
        query_point_list=func_check_data_mybatis(statement,2,"select_point_list")
        query_register_block=func_check_data_mybatis(statement,3,"select_register_block")
        if query_all != -1 and query_only_device  != -1 and query_point_list  != -1 and query_register_block  != -1:
          pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        # 
        results_device = MySQL_Select(query_only_device, (id_device,))
        # 
        if type(results_device) == list and len(results_device)>=1:
            pass
        else:           
            print("Error not found data device")
            return -1
     
        results_RBlock= MySQL_Select(query_register_block, (id_device,))
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
     
        while True:
                device_name=results_device[0]["name"]
                slave_ip = results_device[0]["tcp_gateway_ip"]
                slave_port = results_device[0]['tcp_gateway_port']
                slave_ID =  results_device[0]['rtu_bus_address']     
                try:
                    with ModbusTcpClient(slave_ip, port=slave_port) as client:
                        Data = []
                        for itemRB in results_RBlock:
                            FUNCTION = itemRB["Function"]
                            ADDR = itemRB["addr"]
                            COUNT = itemRB["count"]
                            result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ID)
                            if result_rb==[]:
                                print("The device does not return results")
                            else:
                                if not result_rb.isError():
                                    INC = ADDR-1
                                    for itemR in result_rb.registers:
                                        INC = INC+1
                                        Data.append({"MRA": INC, "Value": itemR})
                                else:            
                                    print("Error ------------------------------------")
                                    print(f'ADDR: {ADDR} COUNT: {COUNT}')
                                    # Exception Response(131, 3, IllegalAddress)
                                    print(result_rb.function_code)
                                    #
                                    print(f"Error reading from {slave_ip}: {result_rb}")
                        new_Data = [x for i, x in enumerate(Data) if x['MRA'] not in {y['MRA'] for y in Data[:i]}]
                        # print(f"Register Block {slave_ip}: {new_Data}")  
                        point_list = []
                        for itemP in results_Plist:
                            result= convert_register_to_point_list(itemP,new_Data)
                            point_list.append(result)
                            # time.sleep(1)
                        print("-----------------Result point_list--------------------------------")
                        for item in point_list:
                            if item["Quality"]==0:
                                print(f'item: {item}')
                        time.sleep(5)
                        # 
                        func_mqtt_public(MQTT_BROKER,
                                         MQTT_PORT,
                                         MQTT_TOPIC+device_name,
                                         MQTT_USERNAME,
                                         MQTT_PASSWORD,
                                         point_list)
                        
                except (ConnectionException, ModbusException) as e:
                    print(f"Modbus error from {slave_ip}: {e}")
                    time.sleep(5)
                except AttributeError as ae:
                    print("AE ERROR", ae)
                    time.sleep(5)

    except Exception as e:
      print('Error : ',e)
   

device(arr)
