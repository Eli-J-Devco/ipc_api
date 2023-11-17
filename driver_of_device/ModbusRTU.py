

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

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import mqttools
import mybatis_mapper2sql
# import paho.mqtt.publish as publish
from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

from config import *
from libMySQL import *

arr = sys.argv
print(f'arr: {arr}')
MQTT_BROKER = Config.MQTT_BROKER
MQTT_PORT = Config.MQTT_PORT
# Publish   -> IPC@device_name
# Subscribe -> IPC@device_name@control
MQTT_TOPIC = Config.MQTT_TOPIC 
MQTT_USERNAME = Config.MQTT_USERNAME
MQTT_PASSWORD =Config.MQTT_PASSWORD
query_device_rs485=""
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
   

async def device(ConfigPara):
    try:
        if len(ConfigPara)>=2 and type(ConfigPara) == list :
            pass
        else:
            return -1
        global query_device_rs485
        pathSource=ConfigPara[2]
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
        serialport_name=results_device[0]["serialport_name"]
        serialport_baud=int(results_device[0]["serialport_baud"])
        serialport_stopbits=int(results_device[0]["serialport_stopbits"])
        serialport_parity=results_device[0]["serialport_parity"][0]
        serialport_timeout=int(results_device[0]["serialport_timeout"])
        print(f'serialport_name: {serialport_name}')
        print(f'serialport_baud: {serialport_baud}')
        print(f'serialport_stopbits: {serialport_stopbits}')
        print(f'serialport_parity: {serialport_parity}')
        print(f'serialport_timeout: {serialport_timeout}')
        # 
        results_RBlock_ManyDevice=[]
        results_Plist_ManyDevice=[]
        print(f'----- results_device -----')
        for item in results_device:
            print(item)
        print(f'----- +++++++++++++++++++++++++++++++++ -----')
        for item in results_device:
            item_rs485= MySQL_Select(query_register_block, (item['id'],))
            # results_RBlock_ManyDevice.append(item_rs485)
            new_item_rs485=[]
            for new_item in item_rs485:
                new_item["rtu_bus_address"] =item["rtu_bus_address"]               
                new_item_rs485.append(new_item)            
            results_RBlock_ManyDevice.append(new_item_rs485)
                
        for item in results_device:
            item_rs485= MySQL_Select(query_point_list, (item['id'],))
            results_Plist_ManyDevice.append(item_rs485)
        
              
            
        # 
        print(f'----- results_RBlock_ManyDevice -----')
        for item in results_RBlock_ManyDevice:
            print(item)
        print(f'----- results_Plist_ManyDevice -----')
        for item in results_Plist_ManyDevice:
            print(item)
        # 
        if type(results_RBlock_ManyDevice) == list and len(results_RBlock_ManyDevice)>=1:
            pass
        else:           
            print("Error device register not found")
            # return -1
        # Check the point list Modbus
        if type(results_Plist_ManyDevice) == list and len(results_Plist_ManyDevice)>=1:
            pass
        else:           
            print("Error device point list not found")
        while True:
            try:
                client = ModbusSerialClient(method="rtu", port=serialport_name, 
                                            stopbits=serialport_stopbits, 
                                            bytesize=8, 
                                            parity=serialport_parity, 
                                            baudrate=serialport_baud,
                                            strict=False)
                connection = client.connect()
            
                if connection:
                    # result_rb  = client.read_holding_registers(1, 4, unit=1) # start_address, count, slave_id
                    
                    print(f'----- Get register -----')
                    device_data=[]
                    for itemRB_Many in results_RBlock_ManyDevice:
                        Data = []
                        status_rb=[]
                        
                        for itemRB in itemRB_Many:
                            device_name_rs485=itemRB["name"]
                            slave_ip=itemRB["rtu_bus_address"]
                            await asyncio.sleep(0.5)
                            FUNCTION = itemRB["Functions"]
                            ADDR = itemRB["addr"]
                            COUNT = itemRB["count"]
                            print('----------- itemRB ---------------------')
                            print(itemRB)
                            result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ip)
                            try:          
                                if result_rb==[]:
                                        print("The device does not return results")
                                else:
                                    if not result_rb.isError():
                                        INC = ADDR-1
                                        for itemR in result_rb.registers:
                                            INC = INC+1
                                            Data.append({"MRA": INC, "Value": itemR, })
                                    else:
                                        
                                        print("Error ------------------------------------")
                                        print(f'Name: {device_name_rs485 } ADDR: {ADDR} COUNT: {COUNT} ')
                                        # Exception Response(131, 3, IllegalAddress)
                                        print(f'ERROR CODE: {result_rb.function_code}')
                                        #
                                        print(f"Error reading from {slave_ip} : {result_rb}")
                                        # status_rb.append({"ADDR":ADDR,
                                        #                       "ERROR_CODE":result_rb.function_code,
                                        #                        "Timestamp": getUTC(),
                                        #                       })
                                        
                            except AttributeError as ae:
                              print('An exception occurred',err)
                              
                        new_Data = [x for i, x in enumerate(Data) if x['MRA'] not in {y['MRA'] for y in Data[:i]}]
                        print(f'----- Value new_Data -----')
                        print(new_Data)
                        device_data.append(new_Data)
                    print(f'----- Value register -----')
                    print(device_data)
                    # if not result_rb.isError():
                    #     print(result_rb.registers)
                    # else:
                    #     # print(f'ERROR CODE: {result_rb.function_code}')
                    #     print('Modbus Error:', result_rb) 
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
async def main():
    tasks = []
    tasks.append(asyncio.create_task(device(arr)))
    await asyncio.gather(*tasks, return_exceptions=False)
if __name__ == '__main__':
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # use for windows
    asyncio.run(main())