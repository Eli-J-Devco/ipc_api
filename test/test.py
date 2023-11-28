import datetime
import time

import pandas as pd

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
listpost =[
   {
      "post_id":"01",
      "text":"abc",
      "time": datetime.datetime(2021, 8, 5, 15, 53, 19),
      "type":"normal",
   },
   {
      "post_id":"02",
      "text":"nothing",
      "time":datetime.datetime(2021, 8, 5, 15, 53, 19),
      "type":"normal",
   }
]
result=list(filter(lambda x: x.get('text', '')=='abc', listpost))
print(result)
