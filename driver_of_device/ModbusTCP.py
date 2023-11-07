
import os
import sys
import time

sys.path.insert(1, "./")
import mybatis_mapper2sql
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

config = sys.argv
# config[0] -- id
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
    xml=os.path.abspath(os.getcwd()) + '/mybatis/device_list.xml')
query = mybatis_mapper2sql.get_child_statement(
    mapper, 'selectOneDeviceList', reindent=True, strip_comments=False)


from libMySQL import *

print(f'config: {config}')


def read_modbus_data(ConfigParameters):
    print(f'Parameter: {ConfigParameters[1]}')

    results = MySQL_Select(query, (ConfigParameters[1],))
    print(f'results: {len(results)}')
    print(f'results: {results[0]}')
    # obj = eval(ConfigParameters)
    slave_ip = ""
    # slave_port = obj['GatewayPort']
    # slave_ID = obj['RTUBusAddress']

    while True:
        try:
            print("read data from device")
            time.sleep(5)
        except (ConnectionException, ModbusException) as e:
            print(f"Modbus error from {slave_ip}: {e}")
        except AttributeError as ae:
            print("AE ERROR", ae)


read_modbus_data(config)
