# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, insert, join, literal_column, select, text

# import api.domain.deviceGroup.models as deviceGroup_models
# import api.domain.deviceList.models as deviceList_models
# import api.domain.project.models as project_models
# import api.domain.template.models as template_models
# import api.domain.user.models as user_models
# import model.models as models
from async_db.wrapper import async_db_request_handler
from configs.config import orm_provider as db_config
# from database.db import get_db
from database.sql.device import all_query
from utils.mqttManager import mqtt_public, mqtt_public_common, mqttService
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              delete_program_pm2_many, find_program_pm2, path,
                              restart_pm2_change_template, restart_program_pm2,
                              restart_program_pm2_many)

from .devices_entity import Devices as DevicesEntity


class DevicesService:
    def __init__(self,
                    
                    host="127.0.0.1",
                    port=1873,
                    topic="",
                    username="",
                    password="",
                    serial_number="",
                    update_device_list=[]):
        
        self.mqtt_host = host
        self.mqtt_port = port
        self.mqtt_topic = topic
        self.mqtt_username = username
        self.mqtt_password = password
        self.update_device_list=update_device_list
        self.serial_number=serial_number
        self.mqtt_init=mqttService(self.mqtt_host,
                    self.mqtt_port,
                    self.mqtt_username,
                    self.mqtt_password,
                    self.serial_number)
    @async_db_request_handler    
    async def create_dev_tcp(self, create_devices,session: AsyncSession):
        try: 
            # data of device
            # {
            #     "CODE": "CreateTCPDev", 
            #     "PAYLOAD":
            #         { 
            #             "device":[
            #             {
            #                 "id":item.id,
            #                 "name":item.name,
            #                 "connect_type":driver_list.name,
            #                 "id_communication":id_communication,
            #                 "mode":item.mode
            #             }
            #                 ]
            #         }
            # }
            new_device=create_devices['device']
            # Insert Device to MQTT
            device_list=[]
            for item_device in new_device:
                have_device=False
                print(f'item_device: {item_device}')
                for item in self.update_device_list:
                    if item_device["id"]!=item["id_device"]:
                        have_device=True
                if have_device:
                    self.update_device_list.append({
                        "id_device":item_device["id"],
                        "device_name":item_device["name"],
                        "mode":item_device["mode"],
                        "parameters":[],
                        "rated_power":item_device["rated_power"]  if 'rated_power' in item_device.keys() else 0,
                        "rated_power_custom":item_device["rated_power_custom"]  if 'rated_power_custom' in item_device.keys() else 0,
                        "min_watt_in_percent" :  item_device["min_watt_in_percent"]  if 'min_watt_in_percent' in item_device.keys() else 0,
                    })
                    device_list.append({
                        "id_device": item_device["id"],
                        "mode":item_device["mode"]
                    })
                #   x >5 ? 4,4 
            #  init start pm2 new app
            for item in new_device:
                
                pid = f'Dev|{item["id_communication"]}|{item["connect_type"]}|{item["id"]}|{item["name"]}'
                await create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,item["id"])
                
            # restart pm2 app log
            pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
            await restart_program_pm2_many(pm2_app_list)
            # 
            # device_id=[296,303]
            # print(f'device_id: {device_id}')
            if device_list:
                id_device = [item["id_device"] for item in device_list]
                query = (update(DevicesEntity)
                    .where(DevicesEntity.id.in_(id_device))
                    .where(DevicesEntity.creation_state == -1)
                    .values(creation_state=0))
                await session.execute(query)    
                await session.commit()
            if device_list:
                await self.mqtt_init.send("Control/Write",
                               device_list)
                
        except Exception as e:
            print("Error create_dev_tcp: ", e)
    @async_db_request_handler
    async def create_dev_rs485(self, create_devices,session: AsyncSession):
        try:
            
            #  data of device
            # {
            #     "CODE": "CreateRS485Dev", 
            #     "PAYLOAD": 
            #         {
            #             "id_communication":id_communication,
            #             "device":[
            #                 {
            #                     "id":item.id,
            #                     "name":item.name,
            #                     "connect_type":driver_list.name,
            #                     "id_communication":id_communication,
            #                     "mode":item.mode
            #                 }
            #             ]
            #         }
            # }
            new_device=create_devices['device']
            device_list=[]
            id_communication=create_devices['id_communication']
            for item_device in new_device:
                have_device=False
                print(f'item_device: {item_device}')
                for item in self.update_device_list:
                    if item_device["id"]!=item["id_device"]:
                        have_device=True
                if have_device:
                    device_list.append({
                        "id_device": item_device["id"],
                        "mode":item_device["mode"]
                    })
                    self.update_device_list.append({
                        "id_device":item_device["id"],
                        "device_name":item_device["name"],
                        "mode":item_device["mode"],
                        "parameters":[]
                    })
            # 
            result_find_app_pm2= find_program_pm2(f'Dev|{str(id_communication)}|')
            if result_find_app_pm2==100:
                await delete_program_pm2(f'Dev|{str(id_communication)}|') 
                # device_list_query = db.query(
                #             deviceList_models.Device_list).filter(
                #             deviceList_models.Device_list.id_communication ==
                #                                         id_communication).filter(
                #             deviceList_models.Device_list.status == 1).order_by(
                #                                         deviceList_models.Device_list.id.asc()).all()
                # db.commit()
                query ='SELECT * FROM `device_list` where id_communication={id_communication} ORDER BY id asc'.format(id_communication=id_communication)
                result_device_list = await session.execute(text(query))
                device_list_query = result_device_list.all()
                results_device_list_dict = [row._asdict() for row in device_list_query]
                
                # check device same group rs485 com port   
                item_rs485 = [item for item in results_device_list_dict if item["id_communication"] == 
                                id_communication]
                
                if item_rs485:
                    # check group rs485 same com port
                    sql_query_select_device=all_query.select_all_device_communication.format(id_communication=id_communication)
                    result= await session.execute(text(sql_query_select_device))
                    result_device_group_rs485 = result.all()
                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                    
                    # init restart pm2 app same rs485
                    await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                    # restart pm2 app log
                    pm2_app_list=[f'LogFile|',f'UpData|']
                    await restart_program_pm2_many(pm2_app_list) 
            elif result_find_app_pm2!=100:
                print('---------- create group RS485 same com port when list device empty ----------')
                # check group rs485 same com port
                sql_query_select_device=all_query.select_all_device_communication.format(id_communication=id_communication)         
                result= await session.execute(text(sql_query_select_device))
                result_device_group_rs485 = result.all()
                results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                
                # init restart pm2 app same rs485
                await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                # restart pm2 app log
                pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
                await restart_program_pm2_many(pm2_app_list)
            else:
                pass
            if device_list:
                id_device = [item["id_device"] for item in device_list]
                query = (update(DevicesEntity)
                    .where(DevicesEntity.id.in_(id_device))
                    .where(DevicesEntity.creation_state == -1)
                    .values(creation_state=0))
                await session.execute(query)    
                await session.commit()
            if device_list:
                await self.mqtt_init.send("Control/Write",
                               device_list)
        except Exception as e:
            print("Error create_dev_rs485: ", e)
        finally:
            # print('create_dev_rs485 end')
            await session.close()
    @async_db_request_handler
    async def delete_dev(self, delete_devices,session: AsyncSession):
        try:
            # data of device
            # mode == 1:  # Disable
            # mode == 2:  # Delete
            # {
            #     "CODE":"DeleteDev",
            #     "PAYLOAD":{
            #         "device":[
            #             {
            #             "mode": mode,
            #             "id": item.id,
            #             "name": device.name,
            #             "id_communication": id_communication,
            #             "connect_type": driver_name,
            #             }
            #             ],
            #         "delete_mode":mode
            #     }
                
            # }
            
            device=delete_devices['device']
            device_tcp=[]
            device_rs485=[]
            communication_list=[]
            id_device=[]
            print(device)
            for item in device:
                id_device.append(item['id'])
                if 'device_type_value' in item.keys():
                    if item["connect_type"]==1:
                        pass
                    else:
                        if item["connect_type"]=="RS485":
                            communication_list.append(item['id_communication'])
                        elif item["connect_type"]=="Modbus/TCP":
                            device_tcp.append(f'Dev|{item["id_communication"]}|Modbus/TCP|{item["id"]}')
            if self.update_device_list:
                if id_device:
                    for item_delete in id_device:
                        for index, msg in enumerate(self.update_device_list):
                            if msg['id_device'] == item_delete:
                                del self.update_device_list[index]
            if device_tcp:
                await delete_program_pm2_many(device_tcp)
                # restart pm2 app log
                pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
                await restart_program_pm2_many(pm2_app_list)
            if communication_list:
                device_rs485=list(set(communication_list))
                print(f'device_rs485: {device_rs485}')
            if device_rs485:
                device_list=[]
                for item in device_rs485:
                    device_list.append(f'Dev|{str(item)}|')
                if device_list:
                    await delete_program_pm2_many(device_list)
                if device_list:
                    for item in device_rs485:
                        id_communication=item
                        sql_query_select_device=all_query.select_all_device_communication.format(id_communication=id_communication)
                        result= await session.execute(text(sql_query_select_device))
                        result_device_group_rs485 = result.all()
                        results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                        
                        # init restart pm2 app same rs485
                        if results_device_group_dict:
                            await create_device_group_rs485_run_pm2(path,results_device_group_dict)
                if device_list:
                    # restart pm2 app log
                    pm2_app_list=[f'LogFile|',f'UpData|',f'LogDevice']
                    await restart_program_pm2_many(pm2_app_list)
            if id_device:
                delete_device_list=[]
                for item in id_device:
                    delete_device_list.append(
                        {
                            "id_device": item,
                            "code":"delete"
                        }
                    )
                print(f'delete_device_list{delete_device_list}')
                await self.mqtt_init.send("Control/Write",
                                delete_device_list)
                await self.mqtt_init.send("Control/Writes",
                                delete_device_list)
        except Exception as e:
            print("Error delete_dev: ", e)
        finally:
            print('delete_dev end')
            await session.close() 
    @async_db_request_handler
    async def update_dev(self, update_devices,session: AsyncSession):
        try:
            {
                "CODE": "UpdateDev", 
                "PAYLOAD":
                    { 
                       "id":296
                    }
            }
            
            id_device=update_devices['id']
            sql_query_select_device=all_query.select_only_device.format(id_device=id_device)
            
            result= await session.execute(text(sql_query_select_device))
            result_device= result.all()
            
            connect_type=None
            device_type_value=None
            device_type_name=None
            device_name=None
            if result_device:
                results_device_dict = [row._asdict() for row in result_device][0]
                id_communication=results_device_dict["id_communication"]
                connect_type=results_device_dict["connect_type"]
                name_device=results_device_dict["name"]
                device_type_value=results_device_dict["device_type_value"]
                device_type_name=results_device_dict["device_type"]
                device_name=results_device_dict["name"]
            
            if device_type_value:
                for i,item in enumerate(self.update_device_list):
                    if item["id_device"] ==id_device:
                        self.update_device_list[i]["device_name"]=device_name
            else:
                match connect_type:
                    case "RS485":
                        serialport_group=results_device_dict["serialport_group"]
                        pm2_app_list=[f'Dev|{id_communication}|{connect_type}|{serialport_group}']
                        await restart_program_pm2_many(pm2_app_list)
                    case "Modbus/TCP":
                        pm2_app_list=[f'Dev|{id_communication}|{connect_type}|{id_device}']
                        await delete_program_pm2_many(pm2_app_list)
                        pid=f'Dev|{id_communication}|{connect_type}|{id_device}|{name_device}'
                        await create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,id_device)
        except Exception as e:
            print("Error update_dev: ", e)
        finally:
            print('update_dev end')
            await session.close() 
    # @staticmethod
    @async_db_request_handler
    async def create_dev_no_log(self, create_devices,session: AsyncSession):
        try:
            new_device=create_devices['device']
            # Insert Device to MQTT
            device_list=[item["id_device"] for item in self.update_device_list]
            for item_device in new_device:
                if len(device_list):
                    if  item_device["id"] in device_list:
                        pass
                    else:
                        self.update_device_list.append({
                        "id_device":item_device["id"],
                        "device_name":item_device["name"],
                        "mode":None,
                        "parameters":[],
                    })
                else:
                    self.update_device_list.append({
                        "id_device":item_device["id"],
                        "device_name":item_device["name"],
                        "mode":None,
                        "parameters":[],
                    })
        except Exception as e:
            print("Error create_dev_no_log: ", e)
        finally:
            print('create_dev_no_log end')
            await session.close() 