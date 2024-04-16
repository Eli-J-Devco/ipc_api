

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
device_mode=[]
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
                 control_max=None
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
                                                            point_value, 
                                                            1,
                                                            message="Not found register",
                                                            active=point_list_item['active'],
                                                            id_control_group=point_list_item['id_control_group'],
                                                            control_type_input=point_list_item['control_type_input'],
                                                            control_menu_order=point_list_item['control_menu_order'],
                                                            control_min=point_list_item['control_min'],
                                                            control_max=point_list_item['control_max'],
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
                                                value, 
                                                0,
                                                message="",
                                                active=point_list_item['active'],
                                                id_control_group=point_list_item['id_control_group'],
                                                control_type_input=point_list_item['control_type_input'],
                                                control_menu_order=point_list_item['control_menu_order'],
                                                control_min=point_list_item['control_min'],
                                                control_max=point_list_item['control_max'],
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
                                        None, 
                                        0,
                                        message="",
                                        active=point_list_item['active'],
                                        id_control_group=point_list_item['id_control_group'],
                                        control_type_input=point_list_item['control_type_input'],
                                        control_menu_order=point_list_item['control_menu_order'],
                                        control_min=point_list_item['control_min'],
                                        control_max=point_list_item['control_max'],
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
                                        0,
                                        message="",
                                        active=point_list_item['active'],
                                        id_control_group=point_list_item['id_control_group'],
                                        control_type_input=point_list_item['control_type_input'],
                                        control_menu_order=point_list_item['control_menu_order'],
                                        control_min=point_list_item['control_min'],
                                        control_max=point_list_item['control_max'],
                                        )
                return point_list
        
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
        
        print(f"Error MQTT public: '{host}|{topic}|{err}'")
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
        # print(f'id_communication: {id_communication}')
        results_device = MySQL_Select(query_device_rs485, (id_communication,))
        # 
        # print(f'results_device: {results_device}')
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
            data_of_one_device["id_device"]=item['id']
            data_of_one_device["device_name"]=item['name']
            data_of_one_device["name_device_type"]=item['device_type']
            data_of_one_device["id_device_type"]=item['id_device_type']
            data_of_one_device["RB"]=[]
            data_of_one_device["POINT"]=[]
            data_of_one_device["id_template"]=item['id_template']
            control_group=[]
            # 
            results_control_group = MySQL_Select(f'SELECT * FROM point_list_control_group where id_template={item["id_template"]} and status=1', ())
            if results_control_group:
                control_group=[
                    {
                        "id":item["id"],
                        "name":item["name"],
                        "description":item["description"],
                        "fields":[]
                        
                    } for item in results_control_group]
            data_of_one_device["control_group"]=control_group
            # 
            # Register block
            item_rb= MySQL_Select(query_register_block, (item['id_template'],))
            new_item_rb=[]
            if type(item_rb) == list and len(item_rb)>=1:
                for new_item in item_rb:
                    new_item["rtu_bus_address"] =item["rtu_bus_address"]               
                    new_item_rb.append(new_item)
            if type(new_item_rb) == list and len(new_item_rb)>=1:
                data_of_one_device["RB"]=new_item_rb

            
            # Point list
            item_point= MySQL_Select(query_point_list, (item['id'],))
            # print(f'item_point: {item_point}')
            if type(item_point) == list and len(item_point)>=1:
                data_of_one_device["POINT"]=item_point
            # 
            all_device_data_request.append(data_of_one_device)
            device_mode.append({
                "id_device":item['id'],
                "mode":item['mode'],
            })
        # for item in all_device_data_request:
        #     print(item)
        #     print('-----------------------------------------')
        #     pprint(item, sort_dicts=False)
            
            
            

        while True:
            try:
                global all_device_data
                new_data_device=[]
                new_error_data_device=[]
                # all_device_data=[]
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
                        data_one_device["id_device"]=item_device["id_device"]
                        data_one_device["id_device_type"]=item_device["id_device_type"]
                        data_one_device["name_device_type"]=item_device['name_device_type']
                        data_one_device["device_name"]=item_device["device_name"]
                        data_one_device["message"]=""
                        data_one_device["status_register"]=[]
                        data_one_device["fields"]=[]
                        data_one_device["status_device"]=""
                        data_one_device["id_template"]=item_device['id_template']
                        data_rg_one_device = []
                        status_rb=[]
                        status_device=""
                        # Read register block 1 device
                        device_name_rs485=item_device["device_name"]
                        for itemRB in item_device["RB"]:
                            
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
                                        status_device="online"
                                        INC = ADDR-1
                                        for itemR in result_rb.registers:
                                            INC = INC+1
                                            data_rg_one_device.append({"MRA": INC, "Value": itemR, })
                                    else:
                                        print("Error ------------------------------------")
                                        # print(f"Error reading from {slave_ip} : {result_rb}")
                                        status_device="online"
                                        print(f'Name: {device_name_rs485 } ADDR: {ADDR} COUNT: {COUNT} ')
                                        if hasattr(result_rb, 'function_code'):
                                            print(f'ERROR CODE: {result_rb.function_code}')
                                            status_rb.append({"ADDR":ADDR,
                                                              "ERROR_CODE":result_rb.function_code,
                                                               "Timestamp": getUTC(),
                                                              })
                                        else:
                                            print(f'This Slave {device_name_rs485} - [{slave_ip}] was not found')
                                            status_device="offline"
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
                        data_one_device["status_register"]=status_rb
                        data_one_device["fields"]=data_point_list_one_device
                        data_one_device["status_device"]=status_device
                        new_data_device.append(data_one_device)
                    all_device_data=new_data_device 
                else:
                    print(f'----- Can not connect to port -----')
                    if  all_device_data:
                        for item_device in all_device_data:
                            data_one_device={}
                            data_point_list_one_device = []
                            # print("1 +++++++++++++++++++++++++++++++++++")
                            for item in item_device["fields"]:
                                data_point_list_one_device.append(
                                    point_object(
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
                                                quality=1,
                                                timestamp=None,
                                                message="Error Device",
                                                active=item['active'],
                                                id_control_group=item['id_control_group'],
                                                control_type_input=item['control_type_input'],
                                                control_menu_order=item['control_menu_order'],
                                                control_min=item['control_min'],
                                                control_max=item['control_max'],
                                                
                                                )
                                )
                            # print("2 +++++++++++++++++++++++++++++++++++")
                            data_one_device["id_device"]=item_device["id_device"]
                            data_one_device["device_name"]=item_device["device_name"]
                            data_one_device["name_device_type"]=item_device['name_device_type']
                            data_one_device["id_device_type"]=item_device['id_device_type']
                            data_one_device["message"]="Can't connect to modbus RTU"
                            data_one_device["status_register"]=[]
                            data_one_device["fields"]=data_point_list_one_device
                            data_one_device["status_device"]="offline"
                            data_one_device["timestamp"]=getUTC()
                            data_one_device["id_template"]=item_device['id_template']
                            data_one_device["control_group"]=item_device['control_group']
                            new_error_data_device.append(data_one_device)
                    
                    else:
                        for item_device in all_device_data_request:
                            data_one_device={}
                            data_point_list_one_device = []
                            # print(f'POINT: {item_device["POINT"]}')
                            for item in item_device["POINT"]:
                                data_point_list_one_device.append(
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
                                                quality=1,
                                                timestamp=None,
                                                message="Error Device",
                                                active=item['active'],
                                                id_control_group=item['id_control_group'],
                                                control_type_input=item['control_type_input'],
                                                control_menu_order=item['control_menu_order'],
                                                control_min=item['control_min'],
                                                control_max=item['control_max'],
                                                
                                                )
                                )
                            print("-----------------------------------------")
                            data_one_device["id_device"]=item_device["id_device"]
                            data_one_device["device_name"]=item_device["device_name"]
                            data_one_device["name_device_type"]=item_device['name_device_type']
                            data_one_device["id_device_type"]=item_device['id_device_type']
                            data_one_device["message"]="Can't connect to modbus RTU"
                            data_one_device["status_register"]=[]
                            data_one_device["fields"]=data_point_list_one_device
                            data_one_device["status_device"]="offline"
                            data_one_device["timestamp"]=getUTC()
                            data_one_device["id_template"]=item_device['id_template']
                            data_one_device["control_group"]=item_device['control_group']
                            new_error_data_device.append(data_one_device)
                        
                    
                    all_device_data=new_error_data_device
                client.close()
                await asyncio.sleep(5)
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
async def monitoring_device(point_type,serial_number_project,
                            host=[], port=[], username=[], password=[]):
    try:
        while True:
            print(f'-----{getUTC()} monitoring_device -----')
            global all_device_data
            global device_mode
            # pprint(all_device_data, sort_dicts=False)
            # global  device_name,status_Device,msg_device,status_register_block,point_list_device
            if all_device_data:
                for item_data in all_device_data:
                    # 
                    id_device=str(item_data['id_device'])
                    device_name=str(item_data['device_name'])
                    id_device_type=item_data['id_device_type']
                    name_device_type=item_data['name_device_type']
                    status_device=item_data['status_device']
                    message=item_data['message']
                    status_register=item_data['status_register']
                    fields=item_data['fields']
                    id_template=item_data['id_template']
                    # 
                    mode=[item for item in device_mode if item['id_device'] == item_data["id_device"]][0]["mode"]
                    # 
                    new_point=[]
                    new_point_list_device=[]
                    mppt=[]
                    control_group=item_data['control_group']
                    new_control_group=[]
                    
                    # 
                    
                    new_data_device={
                        **item_data,
                            "timestamp":getUTC()
                    }
                    # print(new_data_device)
                    for item_point in new_data_device["fields"]:
                        new_point_list_device.append({
                            **item_point,
                            "timestamp":getUTC()
                        })
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
                    # print(new_point)
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
                    # 
                    for item_group in control_group:
                        new_point_control=[]
                        for point_item in new_point_list_device:
                            if point_item["id_control_group"]==item_group["id"]:
                                new_point_control.append({
                                    **point_item
                                })
                        new_point_control.sort(key=lambda x: x["control_menu_order"])   
                        new_control_group.append({
                            **item_group,
                            "fields":new_point_control
                        })
                    data_device={
                                "id_device":id_device,
                                "mode":mode,
                                "device_name":device_name,
                                "id_device_type":id_device_type,
                                "id_template":id_template,
                                "name_device_type":name_device_type,
                                "status_device":status_device,
                                "timestamp":getUTC(),
                                "message":message,
                                "status_register":status_register,
                                "point_count":len(new_point),
                                "parameters":parameters,
                                "fields":fields,
                                "mppt":mppt,
                                "control_group":new_control_group
                                }
                    data_device_short={
                                "id_device":id_device,
                                "mode":mode,
                                "device_name":device_name,
                                "id_device_type":id_device_type,
                                "id_template":id_template,
                                "name_device_type":name_device_type,
                                "status_device":status_device,
                                "timestamp":getUTC(),
                                "message":message,
                                "status_register":status_register,
                                "point_count":len(new_point),
                                "parameters":parameters,
                                "fields":fields,
                                "mppt":[]
                            }
                    if device_name !="" and serial_number_project!= None:
                        
                        func_mqtt_public(   host[0],
                                            port[0],
                                            serial_number_project+"/"+"Devices/"+""+id_device,
                                            username[0],
                                            password[0],
                                            data_device)
                        func_mqtt_public(   host[0],
                                            port[0],
                                            serial_number_project+"/"+"Shorts/"+""+id_device,
                                            username[0],
                                            password[0],
                                            data_device_short)
                        # 
                        if host[1] != None and port[1]:
                            func_mqtt_public(   host[1],
                                                port[1],
                                                serial_number_project+"/"+"Devices/"+""+id_device,
                                                username[1],
                                                password[1],
                                                data_device)
                
            await asyncio.sleep(2)
        
    except Exception as err:
        print('Error monitoring_device : ',err)
async def main():
    tasks = []
    results_project = MySQL_Select('SELECT * FROM `project_setup`', ())
    results_point_list_type= MySQL_Select('select * from `point_list_type`', ())
    serial_number_project=results_project[0]["serial_number"]
    
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
    
    tasks.append(asyncio.create_task(device(arr)))
    tasks.append(asyncio.create_task(monitoring_device( results_point_list_type,
                                                        serial_number_project,
                                                        MQTT_BROKER_LIST,
                                                        MQTT_PORT_LIST,
                                                        MQTT_USERNAME_LIST,
                                                        MQTT_PASSWORD_LIST
                                                                                        
                                                    )))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())