# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
from pathlib import Path


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
path=path_directory_relative("ipc_api") # name of project
sys.path.append(path)


from passlib.context import CryptContext

from config import Config

# PATH_FILE_NETWORK_INTERFACE=Config.PATH_FILE_NETWORK_INTERFACE
# print(f'PATH_FILE_NETWORK_INTERFACE:{PATH_FILE_NETWORK_INTERFACE}')
# 
# check_file = os.path.isfile(PATH_FILE_NETWORK_INTERFACE)
# 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_file_config_network(ethernet_list,network_interface,pathfile):
  try:
      new_Line=[]
      new_Line.append('network:\n')
      new_Line.append('   version: 2\n')
      new_Line.append('   renderer: networkd\n')
      
      if len(ethernet_list)>0:
        new_Line.append('   ethernets:\n')
        
      for item in ethernet_list:
        if item.id==network_interface["id_ethernet"]:
            # add from api
            new_Line.append(f'      {network_interface["namekey"]}:\n')
            result=item.type_ethernet
            if network_interface["id_type_ethernet_name"]=="dhcp":
                new_Line.append(f'          dhcp4: yes\n')
            elif network_interface["id_type_ethernet_name"]=="none":
                new_Line.append(f'          dhcp4: no\n')
                new_Line.append(f'          addresses: [{network_interface["ip_address"]}/24]\n')
                
                new_Line.append(f'          gateway4: {network_interface["gateway"]}\n')
                if network_interface["allow_dns"]==True:
                    new_Line.append(f'          nameservers:\n')
                    new_Line.append(f'              addresses: [{network_interface["dns1"]}, {network_interface["dns2"]}]\n')
            else:
                new_Line.append(f'          dhcp4: yes\n')
          
        else:
            # add from database
            new_Line.append(f'      {item.namekey}:\n')
            result=item.type_ethernet
            if result.name=="dhcp":
                new_Line.append(f'          dhcp4: yes\n')
            elif result.name=="none":
                new_Line.append(f'          dhcp4: no\n')
                new_Line.append(f'          addresses: [{item.ip_address}/24]\n')
                new_Line.append(f'          gateway4: {item.gateway}\n')
                if item.allow_dns== True:
                    new_Line.append(f'          nameservers:\n')
                    new_Line.append(f'              addresses: [{item.dns1},{item.dns2}]\n')
                
            else:
                new_Line.append(f'          dhcp4: yes\n')
                
      # 
      # pathfile = 'D:\\NEXTWAVE\\project\\ipc_api\\test\\netplan\\01-netcfg.yaml'
      check_file = os.path.isfile(pathfile)
      if check_file:
          fileName = open(pathfile, 'w')
          fileName.writelines(new_Line)
          fileName.close()
      else:
          filename = Path(pathfile)
          filename.touch(exist_ok=True)
          # 
          fileName = open(pathfile, 'w')
          fileName.writelines(new_Line)
          fileName.close()
  except Exception as err:
    print('Error create file config network',err)

def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
