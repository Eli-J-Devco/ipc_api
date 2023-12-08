import datetime
import os
import pathlib
import time
from pathlib import Path, PosixPath, WindowsPath

import pandas as pd
from anyio import sleep

result_rs485_group = [   {'id':4, 'name': 'MFM383A-1', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 1'}, 
              {'id':5, 'name': 'MFM383A-2', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 1'}, 
              {'id':6, 'name': 'MFM383A-3', 'connect_type': 'RS485', 'device_type': 'Production Meter', 'serialport_name': 'RS485 Port 2'} 
             ]
# df = pd.DataFrame(records)
# print(df)
# no_dups = df.drop_duplicates()
# result=no_dups[no_dups.duplicated(keep = False, subset="Name")]
# print(result)
# print(result[0]["Name"])
# students = ['Python', 'R', 'C#', 'Python', 'R', 'Java']

# new_list = []
# new_list.append()
# for one_student_choice in students:
#     if one_student_choice not in new_list:
#         new_list.append(one_student_choice)

# print(new_list)
# result_rs485_list = [x for i, x in enumerate(result_rs485_group) if x['serialport_name'] not in {y['serialport_name'] for y in result_rs485_group[:i]}]
# # print(new_Data)
# data=[]
# for rs485_item in result_rs485_list:
#        item=[]
#        for device_item in result_rs485_group:
#               if rs485_item["serialport_name"]==device_item["serialport_name"]:
#                     item.append({
#                             'id':device_item['id'],
#                             'name':device_item['name'],
#                             'connect_type':device_item['connect_type'],                            
#                             "serialport_name":rs485_item["serialport_name"]
#                            })
#        data.append(item)
# print(data)

# dict_example = {'a': 1, 'b': 2}

# print("original dictionary: ", dict_example)

# dict_example['a'] = 100  # existing key, overwrite
# dict_example['c'] = 3  # new key, add
# dict_example['d'] = 4  # new key, add 

# print("updated dictionary: ", dict_example)


# user={
#     "name":"root",
#     "pass":1234
# }    
# print(user)                 
# modify_user={
#     "pass":4567
# }  
                 
# user|=modify_user
# # 
# print(user)
# print(f'{4+4=}')
# import string

# print(string.punctuation)

# percent=11111111.2567
# print(f'{percent:,.2%}')
# data={
#     "id":1,
#     "name":[{"A":1},{"B":1}],
#     "desc":"2222222222222222222222222222222222222222222"
# }

# from pprint import pprint

# pprint(data, sort_dicts=False)

# my_list=['sp1','sp2','sp3']

# for index, item in enumerate(my_list, 1):
#     print(f'{index} :{item}')
# my_list=[1,1,1,2,3,4]
# import statistics

# print(statistics.mode(my_list))

# list1=[1,2,3]
# list2=[4,5,6]
# list1.extend(list2)
# print(list1)
# data=[
#         {"id":1,
#         "value":[{"tag1":1}]},
#         {"id":2,
#         "value":[{"tag1":23}]}
#       ]
# data={}
# data["ID"]=1
# data["NAME"]="INV1"
# print(data)

import pyuac
import wmi


def change_nic_ip():
    # Obtain network adapters configurations
    nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)

    # First network adapter
    nic = nic_configs[0]

    print(nic.IPAddress[0]) # debug message

    # IP address, subnetmask and gateway values should be unicode objects
    ip = '192.168.2.1'
    subnetmask = '255.255.255.0'

    # Set IP address and subnetmask
    static_ip = nic.EnableStatic(IPAddress=[ip], SubnetMask=[subnetmask])

    if 0 in static_ip:
        print("Successful changing to static IP address!")
    else:
        raise ValueError("Error: Changing to static IP address unsuccessful! Error Code: " + static_ip)

    print(nic.IPAddress[0]) # debug message

    # TODO check if static IP Address is actually correct
def revert_to_automatic_ip():
    # Obtain network adapters configurations
    nic_configs = wmi.WMI().Win32_NetworkAdapterConfiguration(IPEnabled=True)

    # First network adapter
    nic = nic_configs[0]

    # Enable DHCP
    dhcp = nic.EnableDHCP()

    if 0 in dhcp:
        print("Successfully changed to automatic IP configuration!")
    else:
        raise ValueError("Error: Changing to automatic IP address unsuccessful! Error Code: " + dhcp)
# pyuac.runAsAdmin()
# change_nic_ip()
# if not pyuac.isUserAdmin():
#         pyuac.runAsAdmin()
# else:
#         # change_nic_ip()
#         revert_to_automatic_ip()
# if __name__ == '__main__':
#     if not pyuac.isUserAdmin():
#         pyuac.runAsAdmin()
#     else:
#         change_nic_ip()
#         # revert_to_automatic_ip()
#         # # TODO remove
#         # import time
#         # time.sleep(3)

# import mysql.connector
# import pandas as pd
# from mysql.connector import Error

# mydb = mysql.connector.connect(
#   host="192.168.80.161",
#   port=3306,
#   user="ipc",
#   password="@$123654789",
#   database="nextwave_ipc_dev"
# )
# mycursor = mydb.cursor()
# for item in range(1000):
#     print(str(item))
#     table="customers_"+str(item)
#     # result=mycursor.execute(f'CREATE TABLE {table} (name VARCHAR(255), address VARCHAR(255))')
#     result=mycursor.execute(f'DROP TABLE {table}')
#     time.sleep(0.1)

# import os.path

# path = './example.txt'

# check_file = os.path.isfile(path)

# print(check_file)

# try:
#     file = open(fn, 'r')
# except FileNotFoundError:
#     file = open(fn, 'w'


# from pprint import pprint

# import psutil

# result=psutil.net_if_addrs()
# pprint(result, sort_dicts=False)
# {
#   "name": "Ethernet-2",
#   "namekey": "enp2s0",
#   "id_type_ethernet": 250,
#   "allow_dns": true,
#   "ip_address": "192.168.80.161",
#   "subnet_mask": "255.255.255.0",
#   "gateway": "192.168.80.1",
#   "mtu": "",
#   "dns1": "8.8.8.8",
#   "dns2": "8.8.4.4"
# }


# import serial.tools.list_ports as ports

# com_ports = list(ports.comports()) # create a list of com ['COM1','COM2'] 
# for i in com_ports:            
#         print(i.device) # returns 'COMx'
  # print(f'communication_baud :{communication_rs485[0].__dict__}')
    # resultList = list(communication_rs485.items())
    # baud=list(filter(lambda x: x.get('type', '')=='401', communication_rs485))
    # baud=communication_rs485.objects.filter(type==401)
# listpost =[
#    {
#       "post_id":"01",
#       "text":"abc",
#       "time": datetime.datetime(2021, 8, 5, 15, 53, 19),
#       "type":"normal",
#    },
#    {
#       "post_id":"02",
#       "text":"nothing",
#       "time":datetime.datetime(2021, 8, 5, 15, 53, 19),
#       "type":"normal",
#    }
# ]
# result=list(filter(lambda x: x.get('text', '')=='abc', listpost))
# print(result)
import asyncio

import mqttools

# async def subscriber():
#     client = mqttools.Client(host="127.0.0.1", 
#                                 port=1883,
#                                 username= "nextwave", 
#                                 password=bytes("123654789", 'utf-8'))

#     await client.start()
#     await client.subscribe('IPC/#')

#     while True:
#         message = await client.messages.get()

#         if message is None:
#             print('Broker connection lost!')
#             break

#         print(f'Topic:   {message.topic}')
#         print(f'Message: {message.message}')

# asyncio.run(subscriber())
class Card(object):

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit

    def __lt__(self, other):
        return self.rank < other.rank

# hand = [Card(10, 'H'), Card(2, 'h'), Card(12, 'h'), Card(13, 'h'), Card(14, 'h')]
# hand_order = [c.rank for c in hand]  # [10, 2, 12, 13, 14]
data=[{"id":1,"value":1},{"id":4,"value":4},{"id":2,"value":2}]
# hand_sorted = sorted(data)
# hand_sorted_order = [c.id for c in hand_sorted]  # [2, 10, 12, 13, 14]
# print(hand_sorted_order)
# result=sorted(data, key=lambda o: o['id'])
# print(result)
{'rowcount': 0, '_soft_closed': True}

# pathfile = 'D:\\NEXTWAVE\\project\\ipc_api\\test\\11\\11'
# new_Line=["3333"]
# directory = "netplan"
  
# # Parent Directory path 
# parent_dir = pathfile
  
# # Path 
# path = os.path.join(parent_dir, directory) 
  
# # Create the directory 
# try: 
#     os.makedirs(path, exist_ok = True) 
#     print("Directory '%s' created successfully" % directory) 
# except OSError as error: 
#     print("Directory '%s' can not be created" % directory) 
# my_dictionary = {
#   "id_001": 1,
#   "id_002": 2
# }
# print("Before:", my_dictionary)
# my_dictionary["id_003"] = 3
# print("After:", my_dictionary)

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic.types import conint


class DeviceListOut(BaseModel):
    id: Optional[int] = None
    
    name: Optional[str] = None
    # device_virtual: Optional[bool] = None
print(DeviceListOut(id=556))