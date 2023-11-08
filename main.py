# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import subprocess
import sys
import time
from shlex import split
from subprocess import Popen, run

import mybatis_mapper2sql
import pandas as pd
# sys.path.insert(1, "./")
from libMySQL import *
from pathlib import Path
import pathlib
import os

absDirname=os.path.dirname(os.path.abspath(__file__))
#
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
    xml= absDirname + '/mybatis/device_list.xml')

query = mybatis_mapper2sql.get_child_statement(
    mapper, 'select_all_device', reindent=True, strip_comments=False)
results = MySQL_Select(query, ())
for item in results:
    # name of pid pm2=id@name
    id = item["id"]
    name = item["name"]
    pid = f'{id}@{name}'
    print(f'pid: {pid}')
    # call driver ModbusTCP
    if item["connect_type"] == "Modbus/TCP" and item["id"] ==2:
        if sys.platform == 'win32':
            # use run with window
            subprocess.Popen(
                f'pm2 start {absDirname}/driver_of_device/ModbusTCP.py -f  --name "{pid}" -- {id} "{name}"  --restart-delay=10000', shell=True).communicate()
        else:
            # use run with ubuntu
            subprocess.Popen(
                f'pm2 start {absDirname}/driver_of_device/ModbusTCP.py --interpreter python3 -f  --name "{pid}" -- {id} "{name}"  --restart-delay=10000', shell=True).communicate()
      
