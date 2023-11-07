
import time
import sys
import os

from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.constants import Endian
from pymodbus.client.sync import ModbusTcpClient
import mybatis_mapper2sql
sys.path.insert(1, "./")
from libMySQL import *
arr = sys.argv
# config[0] -- id
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
    xml=os.path.abspath(os.getcwd()) + '/mybatis/device_list.xml')

statement = mybatis_mapper2sql.get_statement(
    mapper, result_type='list', reindent=True, strip_comments=True)

query_all = statement[0]["select_all_device"]
query_only_device = statement[1]["select_only_device"]
query_point_list = statement[2]["select_point_list"]
query_register_block = statement[3]["select_register_block"]

print(f'arr: {arr}')
def select_function(client, FUNCTION, ADDRs, COUNT, slave_ID):
    if FUNCTION == 0:  # not used                 
        return []
    if FUNCTION == 1:  # Read Coils
        ADDR = ADDRs                        
        result_rb = client.read_coils(
                            ADDR, COUNT, unit=slave_ID)
        return result_rb
    if FUNCTION == 2:  # Read Discrete Inputs                    
        ADDR = ADDRs
        result_rb = client.read_discrete_inputs(
                            ADDR, COUNT, unit=slave_ID)
        return result_rb
    if FUNCTION == 3:  # Read Holding Registers
        ADDR = ADDRs
        result_rb = client.read_holding_registers(
                            ADDR, COUNT, unit=slave_ID)
        return result_rb
    if FUNCTION == 4:  # Read Input Registers
        ADDR = ADDRs
        result_rb = client.read_input_registers(
                            ADDR, COUNT, unit=slave_ID)
        return result_rb
def convert_register_to_point_list(point_list_item,data_of_register,point_list):
     if point_list_item['value_datatype'] == 3: # Short Signed 16-bit
        result = []
        point_value = None
        for itemD in data_of_register:
            if point_list_item['register'] == itemD["MRA"]:
                result.append(itemD["Value"])
        if len(result) > 0:
            decoder = BinaryPayloadDecoder.fromRegisters(
                                        result, byteorder=Endian.Big, wordorder=Endian.Little)
            point_value = decoder.decode_16bit_int()
        else:
            point_list.append(
                {"ID": point_list_item['id_pointkey'], "NAME":  point_list_item['unit_desc'], "UNITS":  point_list_item['name_units'], "Value":  point_value, "Status": 1})
        if point_value != None:
            point_value=point_value*point_list_item['slope']
            point_list.append({"ID": point_list_item['id_pointkey'], "NAME":  point_list_item['unit_desc'], "UNITS":  point_list_item['name_units'], "Value":  point_value, "Status": 0})
def device(ConfigPara):
    results = MySQL_Select(query_only_device, (ConfigPara[1],))
    print(results)
    if len(results) >0:
        results_RBlock= MySQL_Select(query_register_block, (ConfigPara[1],))
        results_Plist= MySQL_Select(query_point_list, (ConfigPara[1],))
        # print(f'results_rblock: {results_RBlock[0]}')
        # print(f'results_plist: {results_Plist}')

        
        while True:
            slave_ip = results[0]["tcp_gateway_ip"]
            slave_port = results[0]['tcp_gateway_port']
            slave_ID =  results[0]['rtu_bus_address']          
            try:
                with ModbusTcpClient(slave_ip, port=slave_port) as client:
                    Data = []
                    for itemRB in results_RBlock:
                        FUNCTION = itemRB["Function"]
                        ADDR = itemRB["addr"]
                        COUNT = itemRB["count"]
                        result_rb=select_function(client,FUNCTION,ADDR,COUNT,slave_ID)
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
                    print(f"Register Block {slave_ip}: {new_Data}")  
                    point_list = []
                    print(f'results_Plist: {results_Plist[0]["value_datatype"]}')
                    for itemP in results_Plist:
                        if itemP['value_datatype'] == 3: # Short Signed 16-bit
                            result = []
                            point_value = None
                            for itemD in new_Data:
                                if itemP['register'] == itemD["MRA"]:
                                    result.append(itemD["Value"])
                            if len(result) > 0:
                                decoder = BinaryPayloadDecoder.fromRegisters(
                                        result, byteorder=Endian.Big, wordorder=Endian.Little)
                                point_value = decoder.decode_16bit_int()
                            else:
                                point_list.append(
                                    {"ID": itemP['id_pointkey'], "NAME":  itemP['unit_desc'], "UNITS":  itemP['name_units'], "Value":  point_value, "Status": 1})
                            if point_value != None:
                                point_value=point_value*itemP['slope']
                                point_list.append(
                                    {"ID": itemP['id_pointkey'], "NAME":  itemP['unit_desc'], "UNITS":  itemP['name_units'], "Value":  point_value, "Status": 0})
                        
                        if itemP['value_datatype'] == 4: # Word Unsigned 16-bit
                            pass
                        if itemP['value_datatype'] == 5: # Long Signed 32-bit
                            pass
                        if itemP['value_datatype'] == 6: # DWord Unsigned 32-bit
                            pass
                        if itemP['value_datatype'] == 7: # LLong Signed 64-bit
                            pass
                        if itemP['value_datatype'] == 8: # QWord Unsigned 64-bit 
                            pass
                        if itemP['value_datatype'] == 9: # Float 32-bit real value IEEE-754
                            result = []
                            point_value = None
                            for itemD in new_Data:
                                if itemP['register'] == itemD["MRA"]:
                                    result.append(itemD["Value"])
                            for itemD in new_Data:
                                if itemP['register']+1 == itemD["MRA"]:
                                    result.append(itemD["Value"])
                            if len(result) > 0:
                                decoder = BinaryPayloadDecoder.fromRegisters(
                                        result, byteorder=Endian.Big, wordorder=Endian.Big)
                                point_value = decoder.decode_32bit_float()
                            else:
                                point_list.append(
                                    {"ID": itemP['id_pointkey'], "NAME":  itemP['unit_desc'], "UNITS":  itemP['name_units'], "Value":  point_value, "Status": 1})
                            if point_value != None:
                                point_value=point_value*itemP['slope']
                                point_list.append(
                                    {"ID": itemP['id_pointkey'], "NAME":  itemP['unit_desc'], "UNITS":  itemP['name_units'], "Value":  point_value, "Status": 0})
                        if itemP['value_datatype'] == 10: # Double 64-bit real value
                            pass
                    # print(f'list_Point: {point_list}')
                    print("-------------------------------------------------")
                    for item in point_list:
                        if item["Status"]==0:
                            print(f'item: {item}')
                            pass
                     
                    time.sleep(5)
                    
                    
            except (ConnectionException, ModbusException) as e:
                print(f"Modbus error from {slave_ip}: {e}")
                time.sleep(5)
            except AttributeError as ae:
                print("AE ERROR", ae)
                time.sleep(5)


device(arr)
