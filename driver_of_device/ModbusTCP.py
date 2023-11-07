


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


def device(ConfigPara):
    results = MySQL_Select(query_only_device, (ConfigPara[1],))
    print(results)
    if len(results) >0:
        results_rblock= MySQL_Select(query_register_block, (ConfigPara[1],))
        results_plist= MySQL_Select(query_point_list, (ConfigPara[1],))
        print(len(results_rblock))
        print(len(results_plist))
        
        while True:
            slave_ip = results[0]["tcp_gateway_ip"]
            slave_port = results[0]['tcp_gateway_port']
            slave_ID =  results[0]['rtu_bus_address']
            
            
            try:
                with ModbusTcpClient(slave_ip, port=slave_port) as client:
                    print("get device -----------")
                    time.sleep(5)
            except (ConnectionException, ModbusException) as e:
                print(f"Modbus error from {slave_ip}: {e}")
            except AttributeError as ae:
                print("AE ERROR", ae)


device(arr)
