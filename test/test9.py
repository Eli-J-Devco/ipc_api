import os
import sys

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("ipc_api")
sys.path.append(path)
print(path)
from src.utils.libMySQL import *

results_project = MySQL_Select("SELECT MPPT1Voltage, MPPT1Current, MPPT2Voltage, MPPT2Current, `error`, `time` FROM `dev_296` WHERE id_device=296 AND `error`=0 AND `time`>='2024-04-17 07:00:00'  AND `time`<='2024-04-17 08:00:00' AND MPPT1Voltage>0 AND MPPT2Voltage>0;", ())
print(results_project)
irradiance =[]
for item in results_project:
    
    irradiance.append({
        "irr1":item["MPPT1Voltage"]*item["MPPT1Current"],
        "irr2":item["MPPT2Voltage"]*item["MPPT2Current"],
    })
    
print(irradiance)
print(len(irradiance))
irr1=0
irr2=0
for item in irradiance:
    irr1=irr1+item["irr1"]
    irr2=irr2+item["irr2"]
print(f'irr1: {irr1/len(irradiance)/1.2}')
print(f'irr2: {irr2/len(irradiance)/1.2}')

print(f'irr1: {irr1/len(irradiance)}')
print(f'irr2: {irr2/len(irradiance)}')