# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import pathlib
import subprocess
import sys
import time
from pathlib import Path
from shlex import split
from subprocess import Popen, run

import mybatis_mapper2sql
import pandas as pd

# sys.path.insert(1, "./")
from libMySQL import *

absDirname=os.path.dirname(os.path.abspath(__file__))
def init_driver():
    try:
        # load file sql from mybatis
        mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
            xml= absDirname + '/mybatis/device_list.xml')

        statement = mybatis_mapper2sql.get_statement(
        mapper, result_type='list', reindent=True, strip_comments=True)
        # 
        if type(statement) == list and len(statement)>2 and 'select_all_device' not in statement:
            pass
        else:           
            print("Error not found data in file mybatis")
            return -1
        query_all = statement[0]["select_all_device"]
        # 
        results = MySQL_Select(query_all, ())
        if type(results) == list and len(results)>1:
            pass
        else:           
            print("Error not found data device")
            return -1
        for item in results:
            # name of pid pm2=id@name
            id = item["id"]
            name = item["name"]
            # pid = f'{id}@{name}'
            pid = f'{name}'
            print(f'pid: {pid}')
            # call driver ModbusTCP
            if item["connect_type"] == "Modbus/TCP" and item["id"] ==1:
                if sys.platform == 'win32':
                    # use run with window
                    subprocess.Popen(
                        f'pm2 start {absDirname}/driver_of_device/ModbusTCP.py -f  --name "{pid}" -- {id} "{absDirname}" --restart-delay=10000', shell=True).communicate()
                else:
                    # use run with ubuntu/linux
                    subprocess.Popen(
                        f'pm2 start {absDirname}/driver_of_device/ModbusTCP.py --interpreter python3 -f  --name "{pid}" -- {id} "{absDirname}"--restart-delay=10000', shell=True).communicate()
    except Exception as e:
        print('Error init driver: ',e)
def init_logfile():
    while True:
        time.sleep(5)
        print("Initializing log")
init_driver()

