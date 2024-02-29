

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
from utils.libMySQL import *

arr = sys.argv
print(f'arr: {arr}')
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC|device_id|device_name
# Subscribe -> IPC|device_id|device_name|control
MQTT_TOPIC = Config.MQTT_TOPIC +"/Dev/"
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
# 
device_name=""
status_register_block=[]
status_device=""
device_id=""
msg_device=""
point_list_device=[]
enable_write_control=False
query_device_control=""
query_only_device=""
data_write_device=[]
# Set time shutdown of inverter
inv_shutdown_enable=False
inv_shutdown_datetime=""
inv_shutdown_point=[]

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
def point_object(ItemID,Name,Units,Value,Quality,Timestamp=None,MsgError=""):
    
    return {"ItemID": ItemID, 
            "Name": Name, 
            "Units": Units, 
            "Value":  Value, 
            "Timestamp":(lambda x:  getUTC() if x ==None else x) (Timestamp),
            "Quality":Quality,
            "MsgError":MsgError
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
                    point_list=point_object(
                                            # point_list_item['id_pointkey'],
                                            point_list_item['id'], 
                                            point_list_item['unit_desc'], 
                                            point_list_item['name_units'], 
                                            point_value, 
                                            1,
                                            MsgError="Not found register"
                                            )
                if point_value != None:
                    point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                    point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                    point_list=point_object(
                                            # point_list_item['id_pointkey'], 
                                            point_list_item['id'], 
                                            point_list_item['unit_desc'], 
                                            point_list_item['name_units'], 
                                            func_check_float(point_value), 
                                            0)
                    
                    return point_list 
                else:  
                    return point_list
            case 4: # Word Unsigned 16-bit
                return {}
            case 5: # Long Signed 32-bit
                return {}
            case 6: # DWord Unsigned 32-bit
                return {}
            case 7: # LLong Signed 64-bit
                return {}
            case 8: # QWord Unsigned 64-bit 
                return {}
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
                    point_list=point_object(
                                            # point_list_item['id_pointkey'], 
                                            point_list_item['id'], 
                                            point_list_item['unit_desc'], 
                                            point_list_item['name_units'], 
                                            point_value, 
                                            1,
                                            MsgError="Not found register"
                                            )      
                if point_value != None:
                    point_value=func_slope(point_list_item['slopeenabled'],point_list_item['slope'],point_value)
                    point_value=func_Offset(point_list_item['offsetenabled'],point_list_item['offset'],point_value)
                    point_list=point_object(
                                            # point_list_item['id_pointkey'], 
                                            point_list_item['id'], 
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
            # return point_list   
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
        print(f'unit: {unit}')
        print(f'datatype: {datatype}')
        print(f'register: {register}')
        print(f'value: {value}')

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

# Describe functions before writing code
# /**
# 	 * @description read modbus TCP
# 	 * @author vnguyen
# 	 * @since 10-11-2023
# 	 * @param {id_device, path (source run file python)}
# 	 * @return data ()
# 	 */
async def device(ConfigPara):
    try:
        
        if len(ConfigPara)>=2 and type(ConfigPara) == list :
            pass
        else:
            return -1
        global query_device_control,query_only_device
        global data_control
        global inv_shutdown_enable,inv_shutdown_datetime,inv_shutdown_point
        global device_id
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
        query_device_control=func_check_data_mybatis(statement,4,"select_device_control")
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
        inv_shutdown_enable=results_device[0]["enable_poweroff"]
        
        while True:
                # Share data to Global variable
                global status_device
                global device_name,msg_device
                global point_list_device,status_register_block
                global enable_write_control
                global data_write_device

  
                device_name=results_device[0]["name"]
                slave_ip = results_device[0]["tcp_gateway_ip"]
                slave_port = results_device[0]['tcp_gateway_port']
                slave_ID =  results_device[0]['rtu_bus_address']
                try:
                    with ModbusTcpClient(slave_ip, port=slave_port) as client:
                        #
                        if enable_write_control ==True:
                            print("---------- write data from Device ----------")
                            
                            for item in data_write_device:
                                result_write_device= write_modbus_tcp(client,slave_ID,
                                                 item["datatype"],
                                                 item["register"],
                                                 item["value"]
                                                 )
                                if result_write_device["value"]==0:
                                    sql=f'UPDATE device_list SET {item["point"]} = 0 Where id ={id_device}'
                                    MySQL_Update(sql)
                                await asyncio.sleep(1)
                            data_write_device=[]
                            enable_write_control = False
                        if inv_shutdown_enable == 1 and inv_shutdown_datetime!="":
                            print("---------- Control shutdown Inverter ----------")
                            # Check today = time set
                            today = DT.now(
                            datetime.timezone.utc).strftime("%Y-%m-%d")
                            datetime_shutdown = DT.strptime(str(inv_shutdown_datetime), "%Y-%m-%d").date()
                            if str(today)==str(datetime_shutdown) :
                                for item in inv_shutdown_point:
                                    result_write_device= write_modbus_tcp(client,slave_ID,
                                                    item["datatype"],
                                                    item["register"],
                                                    item["value"]
                                                    )
                                    if result_write_device["value"]==0:
                                        sql=f'UPDATE device_list SET {item["point"]} = 0 Where id ={id_device}'
                                        MySQL_Update(sql)
                                    await asyncio.sleep(1)
                                    inv_shutdown_enable=0
                        
                        # 
                        # print("---------- read data from Device ----------")

                        msg_device=""
                        # 
                        Data = []
                        status_rb=[]
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
                                    status_device="ONLINE"
                                    INC = ADDR-1
                                    for itemR in result_rb.registers:
                                        INC = INC+1
                                        Data.append({"MRA": INC, "Value": itemR, })
                                else:
                                    print("Error ------------------------------------")
                                    print(f'ADDR: {ADDR} COUNT: {COUNT}')
                                    if hasattr(result_rb, 'function_code'):
                                        status_device="ONLINE"
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
                                        status_device="OFFLINE"
                                        status_rb.append({"ADDR":ADDR,
                                                              "ERROR_CODE":139,
                                                               "Timestamp": getUTC(),
                                                              })      
                        new_Data = [x for i, x in enumerate(Data) if x['MRA'] not in {y['MRA'] for y in Data[:i]}]
                        # print(f"Register Block {slave_ip}: {new_Data}")  
                        point_list = []
                        for itemP in results_Plist:
                            result= convert_register_to_point_list(itemP,new_Data)
                            if len(result)>0:
                                point_list.append(result)
                            else:
                                pass
                        #    
                        point_list_device=point_list
                        
                        # 
                        await asyncio.sleep(5)
                        # 
                except (ConnectionException, ModbusException) as e:
                    # print(f'Loi thiet bi')

                    status_device="OFFLINE"
                    print(f"Modbus error from {slave_ip}: {e}")
                    msg_device=f"{slave_ip}: {e}"
                    # set value Quality of Point =1 when disconnect
                    point_list_error=[]
                    for item in point_list_device:
                       point_list_error.append(point_object(
                                            item['ItemID'], 
                                            item['Name'], 
                                            item['Units'], 
                                            item['Value'], 
                                            1,
                                            item['Timestamp'], 
                                            MsgError="Error Device"
                                            ))
                    point_list_device=point_list_error
                    await asyncio.sleep(5)
                except AttributeError as ae:
                    print("AE ERROR", ae)
                    await asyncio.sleep(5)

    except Exception as err:
        
        print('Error device : ',err)
        
# Describe functions before writing code
# /**
# 	 * @description MQTT public status of device
# 	 * @author vnguyen
# 	 * @since 14-11-2023
# 	 * @param {host, port,topic, username, password, device_name}
# 	 * @return data ()
# 	 */
async def monitoring_device(host, port,topic, username, password
                       
                       ):
    try:
        while True:
            print(f'-----{getUTC()} monitoring_device -----')
            # print("Status Device ---------------------")
            global  device_name,status_device,msg_device,status_register_block,point_list_device
            global device_id
            data_mqtt={
                "ID_DEVICE":device_id,
                "STATUS_DEVICE":status_device,
                "TIME_STAMP":getUTC(),
                "MSG_DEVICE":msg_device,
                "STATUS_REGISTER":status_register_block,
                "POINT_COUNT":len(point_list_device),
                "POINT_LIST":point_list_device,
                
            }
            if device_name !="":
                func_mqtt_public(   host,
                                    port,
                                    topic+""+device_id+"|"+device_name,
                                    username,
                                    password,
                                    data_mqtt)
            await asyncio.sleep(10)
        
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
async def mqtt_subscribe_controls(host, port,topic, username, password):
    try:
        # {
        #    "DEVICE_NAME":"",
        #    "CODE":1 # enable write parameter control
        # }
       
        global enable_write_control,device_name
        global query_device_control
        global data_write_device
        global inv_shutdown_datetime, inv_shutdown_enable,inv_shutdown_point
        global device_id
        # Topic=f'topic+"@"+{str(device_id)}+"@control"'
        Topic=f'IPC/{str(device_id)}|{str(device_name)}|control'
        print(f'Topic: {Topic}')
        client = mqttools.Client(host=host, 
                                port=port,
                                username= username, 
                                password=bytes(password, 'utf-8'))
        
        await client.start()
        await client.subscribe(Topic)
        while True:
            message = await client.messages.get()

            if message is None:
                print('Broker connection lost!')
                break
            print(f'Topic:   {message.topic}')
            result=json.loads(message.message.decode())
            print(f'Message: {result}')
            if 'DEVICE_NAME' in result.keys() and 'CODE' in result.keys() :
                DEVICE_NAME=result["DEVICE_NAME"]
                CODE=result["CODE"]
                
                print(f'DEVICE_NAME: {DEVICE_NAME}')
                print(f'CODE: {CODE}')
                if DEVICE_NAME==device_name and CODE==1 :
                    # print(f'query_device_control: {query_device_control}')
                    results_device_control = MySQL_Select(query_device_control, (device_name,))
                    print(f'results_device_control: {results_device_control}')
                    
                    if type(results_device_control) == list and len(results_device_control)>=1:
                        data_control=[]
                        enable_p=results_device_control[0]["send_p"]
                        enable_q=results_device_control[0]["send_q"]
                        enable_pf=results_device_control[0]["send_pf"]
                        enable_poweroff=results_device_control[0]["enable_poweroff"]
                        inverter_shutdown=results_device_control[0]["inverter_shutdown"]
                        # 
                        if enable_p==1:
                            data_control.append({
                                "point":"send_p",
                                "datatype":results_device_control[0]["datatype_p"],
                                "register":results_device_control[0]["register_p"],
                                "value":results_device_control[0]["value_p"],
                            })
                        if enable_q==1:
                            data_control.append({
                                 "point":"send_q",
                                "datatype":results_device_control[0]["datatype_q"],
                                "register":results_device_control[0]["register_q"],
                                "value":results_device_control[0]["value_q"],
                            })
                        if enable_pf==1:
                            data_control.append({
                                "point":"send_pf",
                                "datatype":results_device_control[0]["datatype_pf"],
                                "register":results_device_control[0]["register_pf"],
                                "value":results_device_control[0]["value_pf"],
                            })
                        # if enable_poweroff==1:
                        #     today = DT.now(
                        #         datetime.timezone.utc).strftime("%Y-%m-%d")
                        #     datetime_shutdown = DT.strptime(str(inverter_shutdown), "%Y-%m-%d").date()
                        #     if str(today)==str(datetime_shutdown) :
                        #         print("Turn off the inverter")
                        #         data_control.append({
                        #                     "point":"enable_poweroff",
                        #                     "datatype":results_device_control[0]["datatype_p"],
                        #                     "register":results_device_control[0]["register_p"],
                        #                     "value":0,
                        #                 })
                        if enable_poweroff==1:
                            inv_shutdown_datetime=inverter_shutdown
                            
                            item=[]
                            item.append({
                                            "point":"enable_poweroff",
                                            "datatype":results_device_control[0]["datatype_p"],
                                            "register":results_device_control[0]["register_p"],
                                            "value":0,
                                        })
                            inv_shutdown_point=item
                            inv_shutdown_enable=1
                        # if enable_p==1 or  enable_q==1 or enable_pf==1 or enable_poweroff==1 :
                        if enable_p==1 or  enable_q==1 or enable_pf==1  :
                            data_write_device=data_control
                            enable_write_control=True
                        else:
                            pass
                 
    except Exception as err:
       
        print(f"Error MQTT subscribe: '{err}'")
async def mqtt_subscribe_controlsV1(host, port,topic, username, password):
    try:
        # {
        #    "DEVICE_NAME":"",
        #    "CODE":1 # enable write parameter control
        # }
       
        global enable_write_control,device_name
        global query_device_control
        global data_write_device
        global inv_shutdown_datetime, inv_shutdown_enable,inv_shutdown_point
        global device_id
        # Topic=f'topic+"@"+{str(device_id)}+"@control"'
        Topic=f'IPC|{str(device_id)}|{str(device_name)}|control'
        print(f'Topic: {Topic}')
        client = mqttools.Client(host=host, 
                                port=port,
                                username= username, 
                                password=bytes(password, 'utf-8'))
        
        await client.start()
        await client.subscribe(Topic)
        while True:
            message = await client.messages.get()

            if message is None:
                print('Broker connection lost!')
                break
            print(f'Topic:   {message.topic}')
            result=json.loads(message.message.decode())
            print(f'Message: {result}')
            if 'DEVICE_NAME' in result.keys() and 'CODE' in result.keys() :
                DEVICE_NAME=result["DEVICE_NAME"]
                CODE=result["CODE"]
                
                print(f'DEVICE_NAME: {DEVICE_NAME}')
                print(f'CODE: {CODE}')
                if DEVICE_NAME==device_name and CODE==1 :
                    # print(f'query_device_control: {query_device_control}')
                    results_device_control = MySQL_Select(query_device_control, (device_name,))
                    # print(f'results_device_control: {results_device_control}')
                    
                    if type(results_device_control) == list and len(results_device_control)>=1:
                        data_control=[]
                        enable_p=results_device_control[0]["send_p"]
                        enable_q=results_device_control[0]["send_q"]
                        enable_pf=results_device_control[0]["send_pf"]
                        enable_poweroff=results_device_control[0]["enable_poweroff"]
                        inverter_shutdown=results_device_control[0]["inverter_shutdown"]
                        # 
                        if enable_p==1:
                            data_control.append({
                                "point":"send_p",
                                "datatype":results_device_control[0]["datatype_p"],
                                "register":results_device_control[0]["register_p"],
                                "value":results_device_control[0]["value_p"],
                            })
                        if enable_q==1:
                            data_control.append({
                                 "point":"send_q",
                                "datatype":results_device_control[0]["datatype_q"],
                                "register":results_device_control[0]["register_q"],
                                "value":results_device_control[0]["value_q"],
                            })
                        if enable_pf==1:
                            data_control.append({
                                "point":"send_pf",
                                "datatype":results_device_control[0]["datatype_pf"],
                                "register":results_device_control[0]["register_pf"],
                                "value":results_device_control[0]["value_pf"],
                            })
                        # if enable_poweroff==1:
                        #     today = DT.now(
                        #         datetime.timezone.utc).strftime("%Y-%m-%d")
                        #     datetime_shutdown = DT.strptime(str(inverter_shutdown), "%Y-%m-%d").date()
                        #     if str(today)==str(datetime_shutdown) :
                        #         print("Turn off the inverter")
                        #         data_control.append({
                        #                     "point":"enable_poweroff",
                        #                     "datatype":results_device_control[0]["datatype_p"],
                        #                     "register":results_device_control[0]["register_p"],
                        #                     "value":0,
                        #                 })
                        if enable_poweroff==1:
                            inv_shutdown_datetime=inverter_shutdown
                            
                            item=[]
                            item.append({
                                            "point":"enable_poweroff",
                                            "datatype":results_device_control[0]["datatype_p"],
                                            "register":results_device_control[0]["register_p"],
                                            "value":0,
                                        })
                            inv_shutdown_point=item
                            inv_shutdown_enable=1
                        # if enable_p==1 or  enable_q==1 or enable_pf==1 or enable_poweroff==1 :
                        if enable_p==1 or  enable_q==1 or enable_pf==1  :
                            data_write_device=data_control
                            enable_write_control=True
                        else:
                            pass
                 
    except Exception as err:
       
        print(f"Error MQTT subscribe: '{err}'")

# Describe functions before writing code
# /**
# 	 * @description check device control
# 	 * @author vnguyen
# 	 * @since 15-11-2023
# 	 * @param {}
# 	 * @return data ()
# 	 */
async def check_device_control():
    try:
        
        while True:
            global enable_write_control,device_name
            global query_device_control
            global data_write_device
            print(f'-----{getUTC()} Check control parameters -----')
           
            results_device_control = MySQL_Select(query_device_control, (device_name,))
           
            if type(results_device_control) == list and len(results_device_control)>=1 and enable_write_control==False:
                data_control=[]
                enable_p=results_device_control[0]["send_p"]
                enable_q=results_device_control[0]["send_q"]
                enable_pf=results_device_control[0]["send_pf"]
                enable_poweroff=results_device_control[0]["enable_poweroff"]
                inverter_shutdown=results_device_control[0]["inverter_shutdown"]
                
                # 
                if enable_p==1:
                                data_control.append({
                                    "point":"send_p",
                                    "datatype":results_device_control[0]["datatype_p"],
                                    "register":results_device_control[0]["register_p"],
                                    "value":results_device_control[0]["value_p"],
                                })
                if enable_q==1:
                                data_control.append({
                                    "point":"send_q",
                                    "datatype":results_device_control[0]["datatype_q"],
                                    "register":results_device_control[0]["register_q"],
                                    "value":results_device_control[0]["value_q"],
                                })
                if enable_pf==1:
                                data_control.append({
                                    "point":"send_pf",
                                    "datatype":results_device_control[0]["datatype_pf"],
                                    "register":results_device_control[0]["register_pf"],
                                    "value":results_device_control[0]["value_pf"],
                                })
                
                if enable_poweroff==1:
                    today = DT.now(
                        datetime.timezone.utc).strftime("%Y-%m-%d")
                    datetime_shutdown = DT.strptime(str(inverter_shutdown), "%Y-%m-%d").date()
                    if str(today)==str(datetime_shutdown) :
                        print("Turn off the inverter")
                        data_control.append({
                                    "point":"enable_poweroff",
                                    "datatype":results_device_control[0]["datatype_p"],
                                    "register":results_device_control[0]["register_p"],
                                    "value":0,
                                })

                # 
                if enable_p==1 or  enable_q==1 or enable_pf==1 or enable_poweroff==1 :
                    data_write_device=data_control
                    enable_write_control=True
                else:
                    pass
            await asyncio.sleep(5)

    except Exception as err:
      print(f"Error check_device_control: '{err}'")
async def main():
    tasks = []
    
    tasks.append(asyncio.create_task(device(arr)))
    tasks.append(asyncio.create_task(monitoring_device( MQTT_BROKER,
                                                    MQTT_PORT,
                                                    MQTT_TOPIC,
                                                    MQTT_USERNAME,
                                                    MQTT_PASSWORD
                                                                                        
                                                    )))
    tasks.append(asyncio.create_task(mqtt_subscribe_controls(MQTT_BROKER,
                                                             MQTT_PORT,
                                                             MQTT_TOPIC,
                                                             MQTT_USERNAME,
                                                             MQTT_PASSWORD
                                                             )))
    # tasks.append(asyncio.create_task(check_device_control()))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    

