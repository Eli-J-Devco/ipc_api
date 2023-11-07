import os
import subprocess
import sys
import time
from shlex import split
from subprocess import Popen, run

import mybatis_mapper2sql
import pandas as pd

from libMySQL import *

#
mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(
    xml=os.path.abspath(os.getcwd()) + '/mybatis/device_list.xml')

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
    if item["connect_type"] == "Modbus/TCP":

        subprocess.Popen(
            f'pm2 start {os.path.abspath(os.getcwd())}/driver_of_device/ModbusTCP.py -f  --name "{pid}" -- {id} "{name}"  --restart-delay=3000', shell=True).communicate()
