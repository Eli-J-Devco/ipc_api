# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import ipaddress
import json
import os
import sys
from pprint import pprint
from typing import Annotated, Optional, Union

import mybatis_mapper2sql
# import oauth2
# import schemas
from async_timeout import timeout
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
# import models
# import utils

import api.domain.deviceGroup.models as deviceGroup_models
import api.domain.deviceList.models as deviceList_models
import api.domain.deviceList.schemas as deviceList_schemas
import api.domain.template.models as template_models
import model.models as models
import utils.oauth2 as oauth2
from database.db import engine, get_db
from utils.libCom import get_mybatis
# from model import schemas
# from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
#                    delete_program_pm2, find_program_pm2, get_mybatis, path,
#                    restart_pm2_change_template, restart_program_pm2,
#                    restart_program_pm2_many)
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              find_program_pm2, restart_pm2_change_template,
                              restart_program_pm2, restart_program_pm2_many)

# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
router = APIRouter(
    prefix="/device_list",
    tags=['DeviceList']
)

# /device_list/
# /device_list


# Describe functions before writing code
# /**
# 	 * @description get only device
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceListOut)
# 	 */ 

@router.post('/', response_model=deviceList_schemas.DeviceListOfPointListOut)
def get_only_device(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    # print(f'id: {id}')
    
    # ----------------------
    Device_list = db.query(deviceList_models.Device_list).filter(deviceList_models.Device_list.id == id).first()
    # Device_list=Device_list.__dict__
    # print(f'device_list :{Device_list}')
    # ----------------------
    # result = db.execute(
    # text(f'select * from user')).all()
    # results_dict = [row._asdict() for row in result]
    # print(f'{results_dict}')
    # ----------------------
    if not Device_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return Device_list

# Describe functions before writing code
# /**
# 	 * @description get all device
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {idb}
# 	 * @return data (DeviceListOut)
# 	 */ 

@router.post('/all/', response_model=list[deviceList_schemas.DeviceListShortOut])
def get_all_device( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    # print(f'id: {id}')
    # ----------------------
    Device_list = db.query(deviceList_models.Device_list)
    # Device_list=Device_list.__dict__
    # ----------------------
    if not Device_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device empty")
    # print(Device_list.all()[0].device_type.__dict__)
    # print(Device_list.all()[0].communication.driver_list.__dict__)
    result_device_list=Device_list.all()
    deviceLists=[]
    for item in result_device_list:
        # Port=""
        # if item.communication.driver_list.name=='Modbus/TCP':
        #     Port=f'{item.tcp_gateway_ip}:{item.tcp_gateway_port}@{item.rtu_bus_address}'
        # elif  item.communication.driver_list.name== "RS485":
        #     Port=f'{item.communication.name}@{ str(item.rtu_bus_address).zfill(4)}'
        # else:
        #     pass
        deviceLists.append({
            "id":item.id,
            "name":item.name,
            "rtu_bus_address":item.rtu_bus_address,
            "tcp_gateway_ip":item.tcp_gateway_ip,
            "tcp_gateway_port":item.tcp_gateway_port,
            "status":item.status,
            "device_type_name":item.device_type.name,
            "driver_type":item.communication.driver_list.name
        })
    
    return deviceLists

# Describe functions before writing code
# /**
# 	 * @description get device config
# 	 * @author vnguyen
# 	 * @since 01-12-2023
# 	 * @param {db}
# 	 * @return data (DeviceConfigOut)
# 	 */ 

@router.post('/config/', response_model=deviceList_schemas.DeviceConfigOut)
def get_device_config( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    # print(f'id: {id}')
    # ----------------------
    device_type_query = db.query(models.Device_type)
    if not device_type_query.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device type does not exist")
    device_group_query = db.query(deviceGroup_models.Device_group)
    if not device_group_query.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device group does not exist")
    device_list_query = db.query(deviceList_models.Device_list).order_by(deviceList_models.Device_list.id.asc())
    template_query = db.query(template_models.Template_library).order_by(template_models.Template_library.id.asc())
    
    communication_query = db.query(models.Communication)
    result_device_type=[]
    for item in device_type_query.all():
        result_device_type.append(item.__dict__)
    result_device_group=[]
    for item in device_group_query.all():
        new_item=item.__dict__
        # new_item["templates_library"]=item.templates_library.__dict__
        result_device_group.append(new_item) 
    # result_device_list=[]
    # for item in device_list_query.all():
    #     result_device_list.append(item.__dict__)
    result_communication=[]
    for item in communication_query.all():
        new_item=item.__dict__
        new_item["driver_list"]=item.driver_list.__dict__
        result_communication.append(new_item) 
    result_template=[]   
    for item in template_query.all():
        new_item=item.__dict__
        result_template.append(new_item) 
    # https://docs.sqlalchemy.org/en/14/core/tutorial.html#using-textual-sql
    
    return {
        # "device_list":result_device_list,
        "device_type":result_device_type,
        "device_group":result_device_group,
        "communication":result_communication,
        "template":result_template
    }
# Describe functions before writing code
# /**
# 	 * @description create device
# 	 * @author vnguyen
# 	 * @since 01-12-2023
# 	 * @param {DeviceCreate,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/create/", response_model=deviceList_schemas.DeviceState)
async def create_device(create_device: deviceList_schemas.DeviceCreate,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    # create_device: list[schemas.DeviceCreate],
    try:
        # format id =
        # create table
        print(f'path: {path}')
        async def execute_func():
            try:
                
                # insert new device to table
                if 'name' in create_device.__dict__.keys():             
                    # 
                    pv=16
                    model=0
                    send_p=0
                    send_q=0
                    send_pf=0
                    value_pf=1       
                    max=100
                    enable_poweroff=0
                    # 
                    # del create_device["driver_list_name"]
                    # 
                    new_device = deviceList_models.Device_list(pv=pv,
                                                    model=model,
                                                    send_p=send_p,
                                                    send_q=send_q,
                                                    send_pf=send_pf,
                                                    value_pf=value_pf,
                                                    max=max,
                                                    enable_poweroff=enable_poweroff,
                                                    **create_device.dict())
                    
                
                    db.add(new_device)
                    db.flush()
                    print(new_device.__dict__)

                    
                    # read file mybatis query sql
    
                    result_mybatis=get_mybatis(path+'/mybatis/device.xml')
                    
                    sql_query=result_mybatis["create_device"]
                    sql_register_block=result_mybatis["insert_device_register_block"]
                    sql_point_list=result_mybatis["insert_device_point_list"]
                    sql_select_device=result_mybatis["select_all_device"]
                    
                    id=new_device.id
                    id_communication=new_device.id_communication
                    # create table new device
                    name_device=f'dev_{str(id).zfill(5)}'
                    sql = sql_query.replace("table_name",name_device )
                    try:
                        #      
                        result_create_table = db.execute(text(sql))
                        print(result_create_table.__dict__)
                    except exc.SQLAlchemyError as err:
                        # delete device in table device_list
                        print(err.args[0])
                        db.rollback()
                        db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                        db.commit()
                        return 300
                    finally:
                        pass
                    if not id :
                        db.rollback()
                        db.query(deviceList_models.Device_list).filter_by(id=id).delete()

                        return 300        
                    communication_query = db.query(models.Communication).filter(models.Communication.id == id_communication).first()
                    try:                    
                        if communication_query:
                            pass        
                        if communication_query.driver_list:
                            pass
                    except Exception as err:
                        print(err)
                        db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                        db.execute(text(f'DROP TABLE {name_device}'))
                        return 300
                    finally:
                        pass              
                    driver_list=communication_query.driver_list
                        
                        # check TCP/RS485
                    if driver_list.name=="RS485":
                        print('RS485 -------------------------------------------')
                        # insert device_register_block
                        result_register_block = db.execute(text(sql_register_block), params={'id': id})
                        # insert device_point_list
                        result_point_list = db.execute(text(sql_point_list), params={'id': id})
                        print(f'result_register_block: {result_register_block.__dict__}')                                                       
                        print(f'result_point_list: {result_point_list.__dict__}')
                        if result_register_block.rowcount == 0 or result_point_list.rowcount==0:
                            db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                            db.execute(text(f'DROP TABLE {name_device}'))                          
                            return 300
                        db.commit()                          
                        result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')                     
                        
                        if result_find_app_pm2==100:
                            result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')
                            # delete success app pm2
                            if result_delete_app_pm2!=100:
                                db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))
                                return 200                          
                            # check list device and Exclusions device new
                            device_list_query = db.query(
                                deviceList_models.Device_list).filter(deviceList_models.Device_list.id_communication ==
                                                            id_communication).filter(
                                deviceList_models.Device_list.status == 1).order_by(
                                                            deviceList_models.Device_list.id.asc()).all()
                            # check device same group rs485 com port   
                            item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                        id_communication]
                            # find device in group rs485
                            if not item_rs485:
                                db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))
                                return 200 
                            if item_rs485:
                                # check group rs485 same com port
                                result_device_group_rs485 = db.execute(
                                                                            text(sql_select_device), 
                                                                            params={'id_communication': 
                                                                            create_device.id_communication}).all()
                                results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                                if not results_device_group_dict:
                                    db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                                    db.execute(text(f'DROP TABLE {name_device}'))
                                    return 300                                              
                                # init restart pm2 app same rs485
                                create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                # restart pm2 app log
                                return 100                                                              
                        if result_find_app_pm2!=100:
                            print('---------- create group RS485 same com port when list device empty ----------')
                            # check group rs485 same com port 
                            result_device_group_rs485 = db.execute(
                                                                        text(sql_select_device), 
                                                                        params={'id_communication': 
                                                                        id_communication}).all()
                            results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                            if not results_device_group_dict:
                                db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))
                                return 200
                            # init restart pm2 app same rs485
                            create_device_group_rs485_run_pm2(path,results_device_group_dict)
                            # restart pm2 app log
                            return 100                                                                                                                            
                    elif driver_list.name=="Modbus/TCP":
                        print('Modbus/TCP -------------------------------------------')                       
                        try:
                            # insert device_register_block                                
                            result_register_block = db.execute(text(sql_register_block), params={'id': id})
                            print(f'result_register_block: {result_register_block.__dict__}')
                            # insert device_point_list
                            result_point_list = db.execute(text(sql_point_list), params={'id': id})                        
                            print(f'result_point_list: {result_point_list.__dict__}')
                            if result_register_block.rowcount == 0 or result_point_list.rowcount==0:
                                db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))                                                                 
                                return 300 
                            db.commit()
                            # init start pm2 new app
                            name = new_device.name
                            connect_type=driver_list.name
                            pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                            create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,id)
                            # restart pm2 app log
                            return 100
                                                                
                        except exc.SQLAlchemyError as err:
                            # delete device in table device_list
                            print(err.args[0])
                            db.rollback()
                            return 300
                        finally:
                                pass                                             
                    else:
                        return 200                  
            except Exception as err:
                db.rollback()
                print('Error create table : ',err)
                return 300
        async with timeout(5) as cm:
            response=  await execute_func() 
            if response==100:# ok
                return {"status": "success","code": str(response)}
            elif response==200: # alarm
                return {"status": "alert","code": str(response)}
            elif response==300: # error
                return {"status": "error","code": str(response)}
            else:
                return {"status": "error","code": "400"}
        
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")

# Describe functions before writing code
# /**
# 	 * @description create multiple device
# 	 * @author vnguyen
# 	 * @since 11-12-2023
# 	 * @param {DeviceCreate,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/create_multiple/", response_model=deviceList_schemas.DeviceState)
async def create_multiple_device(create_device: deviceList_schemas.MultipleDeviceCreate ,
                                 db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        def reset_data_new(new_device_list):
            # delete device in table device_list
            for items in new_device_list:  
                db.query(models.Device_list).filter_by(id=items.id).delete()
                db.commit()
                print(f'Delete device: {items.id}')
            # delete all table created
            for i,items in enumerate(new_device_list):                                 
                name_device=f'dev_{str(items.id).zfill(5)}'
                db.execute(text(f'DROP TABLE {name_device}'))                                                                                        
            return 300
            
        async def execute_func():
            try:
                
                if not  create_device.in_addcount or not create_device.in_addmode:
                    return 300                                   
                id_communication=create_device.id_communication
                communication_query = db.query(models.Communication).filter(models.Communication.id == id_communication).first()
                
                try:                    
                    if communication_query:
                        pass        
                    if communication_query.driver_list:
                        pass
                except Exception as err:
                    print(err)             
                    return 300
                finally:
                    pass              
                driver_list=communication_query.driver_list
                # insert new device to table
                new_device_list=[]
                in_addcount=create_device.in_addcount
                    
                for item in range(in_addcount):                       
                        pv=16
                        model=0
                        send_p=0
                        send_q=0
                        send_pf=0
                        value_pf=1       
                        max=100
                        enable_poweroff=0
                        # tcp_gateway_ip=create_device.tcp_gateway_ip

                        name=create_device.name
                        device_virtual=create_device.device_virtual
                        id_communication=create_device.id_communication
                        rtu_bus_address=create_device.rtu_bus_address
                        tcp_gateway_port=create_device.tcp_gateway_port
                        tcp_gateway_ip=create_device.tcp_gateway_ip
                        id_device_type=create_device.id_device_type
                        id_device_group=create_device.id_device_group
                        # network address
                        if create_device.in_addmode==1:                           
                            ip = create_device.tcp_gateway_ip.split(".")
                            host_id=int(ip[3])+item
                            if  host_id>=255 :
                                host_id=254
                            tcp_gateway_ip=f'{ip[0]}.{ip[1]}.{ip[2]}.{host_id}'
                            
                        # bus-address
                        elif create_device.in_addmode==2:
                            rtu_bus_address=int(create_device.rtu_bus_address) +item
                            
                        else:
                            return 300 
                        new_device = deviceList_models.Device_list(pv=pv,
                                                        model=model,
                                                        send_p=send_p,
                                                        send_q=send_q,
                                                        send_pf=send_pf,
                                                        value_pf=value_pf,
                                                        max=max,
                                                        enable_poweroff=enable_poweroff,
                                                        name=name,
                                                        device_virtual=device_virtual,
                                                        id_communication=id_communication,
                                                        rtu_bus_address=rtu_bus_address,
                                                        tcp_gateway_port=tcp_gateway_port,
                                                        tcp_gateway_ip=tcp_gateway_ip,
                                                        id_device_type=id_device_type,
                                                        id_device_group=id_device_group                                                                                                                                                                                                                                                               # **create_device.dict()
                                                        )
                        new_device_list.append(new_device)
                db.add_all(new_device_list)
                db.flush()           
            
                # create table new device            
                result_mybatis=get_mybatis(path+'/mybatis/device.xml')
                sql_query=result_mybatis["create_device"]
                sql_register_block=result_mybatis["insert_device_register_block"]
                sql_point_list=result_mybatis["insert_device_point_list"]
                sql_select_device=result_mybatis["select_all_device"]
                
                
                # 
                for idd,item in enumerate(new_device_list):
                        try:
                            
                            name_device=f'dev_{str(item.id).zfill(5)}'
                            sql = sql_query.replace("table_name",name_device)
                            print(f'Device :{item.id} -------------------')
                            #  
                            result_create_table = db.execute(text(sql))
                            print(result_create_table.__dict__)
                        except exc.SQLAlchemyError as err:
                            # delete device in table device_list
                            print(err.args[0])
                            db.rollback()
                            for items in new_device_list:  
                                db.query(models.Device_list).filter_by(id=items.id).delete()
                                db.commit()
                                print(f'Delete device: {items.id}')
                            # delete all table created
                            for i,items in enumerate(new_device_list): 
                                if i<idd:                                
                                    name_device=f'dev_{str(items.id).zfill(5)}'
                                    db.execute(text(f'DROP TABLE {name_device}'))
                                else:
                                    break                              
                            return 300
                        finally:
                            pass
                if driver_list.name=="RS485":
                    
                    try:
                        rowcount_register_block=0
                        rowcount_point_list=0
                        # insert device_register_block 
                        for item in new_device_list:
                            result_register_block = db.execute(text(sql_register_block),params={'id': item.id})
                            print(f'result_register_block: {result_register_block.__dict__}')
                            if result_register_block.rowcount != 0:
                                rowcount_register_block +=1
                        
                        # insert device_point_list
                        for item in new_device_list:
                            result_point_list = db.execute(text(sql_point_list),params={'id': item.id})                        
                            print(f'result_point_list: {result_point_list.__dict__}')
                            if result_point_list.rowcount != 0:
                                rowcount_point_list +=1
                        
                        if rowcount_register_block  == 0 or rowcount_point_list==0:
                            reset_data_new(new_device_list)

                        db.commit()
                        result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')
                        if result_find_app_pm2==100:
                            result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')    
                            # delete success app pm2
                            if result_delete_app_pm2!=100:
                                reset_data_new(new_device_list)
                            # check list device and Exclusions device new
                            device_list_query = db.query(
                                    deviceList_models.Device_list).filter(deviceList_models.Device_list.id_communication ==
                                                                id_communication).filter(
                                    deviceList_models.Device_list.status == 1).order_by(
                                                                deviceList_models.Device_list.id.asc()).all()
                            # check device same group rs485 com port   
                            item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                            id_communication]
                            # find device in group rs485
                            if not item_rs485:
                                reset_data_new(new_device_list) 
                            if item_rs485:
                                # check group rs485 same com port
                                result_device_group_rs485 = db.execute(
                                                                        text(sql_select_device), 
                                                                        params={'id_communication': 
                                                                        id_communication}).all()
                                results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                                if not results_device_group_dict:
                                    reset_data_new(new_device_list)                                             
                                # init restart pm2 app same rs485
                                create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                # restart pm2 app log
                                restart_program_pm2(f'Log')
                                return 100    
                        if result_find_app_pm2!=100:
                            print('---------- create group RS485 same com port when list device empty ----------')
                            # check group rs485 same com port 
                            result_device_group_rs485 = db.execute(
                                                                        text(sql_select_device), 
                                                                        params={'id_communication': 
                                                                        id_communication}).all()
                            results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                            if not results_device_group_dict:
                                reset_data_new(new_device_list)
                            # init restart pm2 app same rs485
                            create_device_group_rs485_run_pm2(path,results_device_group_dict)
                            # restart pm2 app log
                            restart_program_pm2(f'Log')
                            return 100     
                    except exc.SQLAlchemyError as err:
                            # delete device in table device_list
                            print(err.args[0])
                            db.rollback()
                            reset_data_new(new_device_list)
                    finally:
                            pass         
                elif driver_list.name=="Modbus/TCP":              
                
                
                    try:
                        rowcount_register_block=0
                        rowcount_point_list=0
                        # insert device_register_block 
                        for item in new_device_list:
                            result_register_block = db.execute(text(sql_register_block),params={'id': item.id})
                            print(f'result_register_block: {result_register_block.__dict__}')
                            if result_register_block.rowcount != 0:
                                rowcount_register_block +=1
                        
                        # insert device_point_list
                        for item in new_device_list:
                            result_point_list = db.execute(text(sql_point_list),params={'id': item.id})                        
                            print(f'result_point_list: {result_point_list.__dict__}')
                            if result_point_list.rowcount != 0:
                                rowcount_point_list +=1
                        
                        if rowcount_register_block  == 0 or rowcount_point_list==0:
                            reset_data_new(new_device_list)

                        db.commit()
                        
                        # init start pm2 new app
                        for item in new_device_list:
                            name = item.name
                            connect_type=driver_list.name
                            pid = f'Dev|{id_communication}|{connect_type}|{item.id}|{name}'
                            create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,item.id)
                            # restart pm2 app log
                        restart_program_pm2(f'Log')
                        return 100 
                    except exc.SQLAlchemyError as err:
                            # delete device in table device_list
                            print(err.args[0])
                            db.rollback()
                            reset_data_new(new_device_list)
                    finally:
                            pass
                else:
                    return 300 
            except Exception as err:
                print('Error create table : ',err)
                return 300
        async with timeout(500) as cm:
            response=  await execute_func()
            if response==100:# ok
                return {"status": "success","code": str(response)}
            elif response==200: # alarm
                return {"status": "alert","code": str(response)}
            elif response==300: # error
                return {"status": "error","code": str(response)}
            else:
                return {"status": "error","code": "400"}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
# Describe functions before writing code
# /**
# 	 * @description get point list
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {id,db}
# 	 * @return data (DevicePointListBase)
# 	 */
@router.post('/point_list/', response_model=list[deviceList_schemas.DevicePointListBase])
def get_point_list_only_device(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    
    # ----------------------
    device_point_list_query = db.query(models.Device_point_list).filter(
        models.Device_point_list.id_device_list == id).all()
    # 
    if not device_point_list_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with id: {id} does not exist")

    # return {"point_list":device_point_list_query}
    return device_point_list_query


# Describe functions before writing code
# /**
# 	 * @description delete device
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/delete/", response_model=deviceList_schemas.DeviceState)
async def delete_device(
                        delete_device: deviceList_schemas.DeviceDelete,
                        db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        
        if not delete_device.mode in [1,2] :
            return {"status": "error","code": str(300)}
        id=delete_device.id
        device_list_query = db.query(deviceList_models.Device_list).filter(
        deviceList_models.Device_list.id == id).filter(
        deviceList_models.Device_list.status == 1)
        
        result=device_list_query.first()
        if not result:
            return {"status": "error","code": str(300)}
        result_communication=None
        mode=delete_device.mode
        try:
            result_communication=result.communication # accessing a non-existing attribute communication
        except AttributeError as e:
            print(f"AttributeError: {e}")
            return {"status": "error","code": str(300)}
        # print(f'result_communication: {result_communication.__dict__}')
        result_driver=None
        try:
            result_driver=result_communication.driver_list # accessing a non-existing attribute communication
        except AttributeError as e:
            print(f"AttributeError: {e}")
            return {"status": "error","code": str(300)}
        # print(f'result_driver: {result_driver.__dict__}')
        id_communication=result.id_communication
        if result_driver.name == "Modbus/TCP":
            print('delete device TCP ------')
            # Deactivate/delete device TCP ------
            connect_type=result_driver.name
            if mode ==1:
                # Deactivate device in table device_list -----
                device_list_query.filter(deviceList_models.Device_list.id == id).update({"status": 0}, synchronize_session=False)
                db.commit()
                # delete app running in pm2
                result_pm2=delete_program_pm2(f'Dev|{id_communication}|{connect_type}|{id}')
                print(f'result_pm2: {result_pm2}')
                restart_program_pm2(f'Log')
                return {"status": "success","code": str(100)}
            if mode ==2:
                # Delete data device in table device_list -----
                result_delete_device_list =db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                db.commit()
                result_pm2=delete_program_pm2(f'Dev|{id_communication}|{connect_type}|{id}')
                print(f'result_pm2: {result_pm2}')
                restart_program_pm2(f'Log')
                return {"status": "success","code": str(100)}
            
        elif result_driver.name == "RS485":
            result_mybatis=get_mybatis(path+'/mybatis/device.xml')
            sql_query=result_mybatis["create_device"]
            sql_register_block=result_mybatis["insert_device_register_block"]
            sql_point_list=result_mybatis["insert_device_point_list"]
            sql_select_device=result_mybatis["select_all_device"]
            
            if mode ==1:
                # Deactivate device in table device_list -----
                device_list_query.filter(deviceList_models.Device_list.id == id).update({"status": 0}, synchronize_session=False)
                db.commit()
            if mode ==2:   
                # Delete data device in table device_list -----
                result_delete_device_list =db.query(deviceList_models.Device_list).filter_by(id=id).delete()
                db.commit()
            result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')
            if result_find_app_pm2==100:
                result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')
                if result_delete_app_pm2!=100:
                    return {"status": "error","code": str(300)}
                all_device_list_query = db.query(
                                deviceList_models.Device_list).filter(deviceList_models.Device_list.id_communication ==id_communication
                                                            ).filter(
                                deviceList_models.Device_list.status == 1).order_by(
                                                            deviceList_models.Device_list.id.asc()).all()
                item_rs485 = [item.__dict__ for item in all_device_list_query if item.id_communication == 
                                            id_communication]
                
                # find device in group rs485
                if item_rs485:                                 
                    # check group rs485 same com port
                    result_device_group_rs485 = db.execute(
                                                            text(sql_select_device), 
                                                            params={'id_communication': 
                                                            id_communication}).all()
                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                    if results_device_group_dict:
                        # init restart pm2 app same rs485
                        create_device_group_rs485_run_pm2(path,results_device_group_dict)
                        restart_program_pm2(f'Log')
                        return {"status": "success","code": str(100)}
                    else:
                        pass
                else:
                   return {"status": "success","code": str(100)} 
            else:                                                                         
                return {"status": "success","code": str(100)}
                
           
        else: 
            return {"status": "success","code": str(100)}        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
# Describe functions before writing code
# /**
# 	 * @description update device
# 	 * @author vnguyen
# 	 * @since 13-12-2023
# 	 * @param {DeviceUpdateBase,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/update/", response_model=deviceList_schemas.DeviceState)
async def update_device_basic(update_device: deviceList_schemas.DeviceUpdateBase,
                              db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        # need restart pm2
        # name --> allow change
        # id_project_setup --> allow change
        # device_virtual --> lock
        # id_device_type --> lock
        # id_communication --> lock
        # id_device_group if change it
            # - delete all in table device_point_list
            # - delete all in table device_register_block
            # - init parameter in table device_point_list
            # - init parameter in table device_register_block
        # rtu_bus_address --> allow change
        # tcp_gateway_ip --> allow change
        # tcp_gateway_port --> allow change
        
        # chon group khac
            # delete all device_point_list
        # edit point/register block
            # template_library
            # delete all device_point_list
        # --> init app in pm2
        def init_pm2_dev_tcp(id,name,id_communication,connect_type):
            # Find app pm2
            result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|{connect_type}|{id}|')
            if result_find_app_pm2==100:
                # delete success app pm2
                result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|{connect_type}|{id}|')
                if result_delete_app_pm2!=100:
                    return 200
                else:
                    # init start pm2 app
                    pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                    create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,id)
                    return 100
            else:
                # init start pm2 app
                pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                create_program_pm2(f'{path}/deviceDriver/ModbusTCP.py',pid,id)
                return 100
        def init_pm2_dev_rs485(id_communication,sql_select_device):
            result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')
            if result_find_app_pm2==100:
                result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')  
                if result_delete_app_pm2!=100:
                    return 300
                # check list device and Exclusions device new
                device_list_query = db.query(
                        deviceList_models.Device_list).filter(deviceList_models.Device_list.id_communication ==
                                                    id_communication).filter(
                        deviceList_models.Device_list.status == 1).order_by(
                                                    deviceList_models.Device_list.id.asc()).all()
                # check device same group rs485 com port   
                item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                id_communication]
                # # find device in group rs485
                # if not item_rs485:
                #     reset_data_new(new_device_list) 
                if item_rs485:
                    # check group rs485 same com port
                    result_device_group_rs485 = db.execute(
                                                            text(sql_select_device), 
                                                            params={'id_communication': 
                                                            id_communication}).all()
                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]
                    # if not results_device_group_dict:
                    #     reset_data_new(new_device_list)                                             
                    # init restart pm2 app same rs485
                    create_device_group_rs485_run_pm2(path,results_device_group_dict)
                    # restart pm2 app log
                    restart_program_pm2(f'Log')
                    return 100
            elif result_find_app_pm2!=100: 
                print('---------- create group RS485 same com port when list device empty ----------')
                # check group rs485 same com port 
                result_device_group_rs485 = db.execute(
                                                            text(sql_select_device), 
                                                            params={'id_communication': 
                                                            id_communication}).all()
                results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                # if not results_device_group_dict:
                #     reset_data_new(new_device_list)
                # init restart pm2 app same rs485
                create_device_group_rs485_run_pm2(path,results_device_group_dict)
                # restart pm2 app log
                restart_program_pm2(f'Log')
                return 100     
            else:
                return 300
        
        async def execute_func():
            try:
                id=update_device.id
                id_device_group=update_device.id_device_group
                name = update_device.name
                # id_communication
                device_list_query = db.query(deviceList_models.Device_list).filter(deviceList_models.Device_list.id == id)
                result_device_list = device_list_query.first()
                
                if not result_device_list:
                    return 300               
                id_communication=result_device_list.id_communication
                connect_type=result_device_list.communication.driver_list.name
                # 
                result_mybatis=get_mybatis(path+'/mybatis/device.xml')
                sql_register_block=result_mybatis["insert_device_register_block"]
                sql_point_list=result_mybatis["insert_device_point_list"]
                sql_select_device=result_mybatis["select_all_device"]
                # check changed id_device_group, If it changed Re-initialize --> device_point_list and device_register_block
                result_check_id_device_group=db.query(deviceList_models.Device_list).filter(deviceList_models.Device_list.id 
                                                                                == id).filter(deviceList_models.Device_list.id_device_group 
                                                                                == id_device_group).first()
                if not result_check_id_device_group: #Re-initialize
                    try:
                        print(f'Re-initialize --> id: {id}| id_device_group: {id_device_group}|')
                        result_del_device_point_list =db.query(models.Device_point_list).filter_by(id_device_list=id).delete()
                        result_del_device_register_block=db.query(models.Device_register_block).filter_by(id_device_list=id).delete()
                        db.flush()
                        update_data=update_device.dict()
                        device_list_query.filter(deviceList_models.Device_list.id == id).update(update_data, synchronize_session=False)
                        result_register_block = db.execute(text(sql_register_block), params={'id': id})
                        result_point_list = db.execute(text(sql_point_list), params={'id': id})
                        db.flush()                          
                        if (result_del_device_point_list and 
                            result_del_device_register_block 
                            and result_register_block.rowcount > 0 
                            and  result_point_list.rowcount>0):
                            print(f'Delete all point and register block of Device')
                            db.commit()
                            # app pm2
                            if connect_type=="Modbus/TCP":
                                init_pm2_dev_tcp(id,name,id_communication,connect_type)
                                restart_program_pm2(f'Log')
                            elif connect_type=="RS485":
                                init_pm2_dev_rs485(id_communication,sql_select_device)
                            else:
                                return 300   
                                
                    except Exception as err:
                        print(err)
                        db.rollback()

                else: # keep
                    print(f'Update --> id: {id}| id_device_group: {id_device_group}|')
                    update_data=update_device.dict()
                    device_list_query.filter(deviceList_models.Device_list.id == id).update(update_data, synchronize_session=False)
                    db.commit()
                    if connect_type=="Modbus/TCP":
                        init_pm2_dev_tcp(id,name,id_communication,connect_type)
                        restart_program_pm2(f'Log')
                    elif connect_type=="RS485":
                        init_pm2_dev_rs485(id_communication,sql_select_device)
                    else:
                        return 300 

            except Exception as err: 
                print('Error update device : ',err)
                return 300
        async with timeout(5) as cm:
            response=  await execute_func() 
            if response==100:# ok
                return {"status": "success","code": str(response)}
            elif response==200: # alarm
                return {"status": "alert","code": str(response)}
            elif response==300: # error
                return {"status": "error","code": str(response)}
            else:
                return {"status": "error","code": "400"}
        
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
