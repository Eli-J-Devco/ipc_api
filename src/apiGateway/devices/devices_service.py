# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from utils.mqttManager import mqtt_public, mqtt_public_common
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)


class DevicesService:
    def __init__(self,
                    host="127.0.0.1",
                    port=1873,
                    topic="",
                    username="",
                    password="",
                    update_device=[]):
        self.mqtt_host = host
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.mqtt_username = username
        self.mqtt_password = password
        self.update_device=update_device
    async def create_dev_tcp(self, create_devices):
        # print(path)
        new_device=create_devices
        # Insert Device to MQTT
        for item_device in new_device:
            have_device=False
            print(f'item_device: {item_device}')
            for item in self.update_device:
                if item_device["id"]!=item["id_device"]:
                    have_device=True
            if have_device:
                self.update_device.append({
                    "id_device":item_device["id"],
                    "device_name":item_device["name"],
                    "mode":item_device["mode"],
                    "parameters":[],
                    "rated_power":item_device["rated_power"]  if 'rated_power' in item_device.keys() else None,
                    "rated_power_custom":item_device["rated_power_custom"]  if 'rated_power_custom' in item_device.keys() else None,
                    "min_watt_in_percent" :  item_device["min_watt_in_percent"]  if 'min_watt_in_percent' in item_device.keys() else None,
                })
            #   x >5 ? 4,4 
        #  init start pm2 new app
        for item in new_device:
            
            pid = f'Dev|{item["id_communication"]}|{item["connect_type"]}|{item["id"]}|{item["name"]}'
            await create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,item["id"])
        # restart pm2 app log
        pm2_app_list=[f'LogFile|',f'UpData|',f'UpData']
        await restart_program_pm2_many(pm2_app_list)
        # 
        now = datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        param=  {
                    "CODE":"CreateTCPDev",
                    "PAYLOAD":new_device,
                    "TIME_STAMP":now
                }
        mqtt_public("/Init/API/Responses",param)
        print("create_dev_tcp")
    async def create_dev_rs485(self):
        pass