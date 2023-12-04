# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
from pprint import pprint
from typing import Annotated, Union

import models
import mybatis_mapper2sql
import oauth2
import schemas
import utils
from async_timeout import timeout
from database import get_db
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException,
                     Response, status)
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
                   delete_program_pm2, path, restart_program_pm2)

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

@router.get('/', response_model=schemas.DeviceListOut)
def get_only_device(id: int, db: Session = Depends(get_db), ):
    # print(f'id: {id}')
    # ----------------------
    Device_list = db.query(models.Device_list).filter(models.Device_list.id == id).first()
    Device_list=Device_list.__dict__
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

@router.get('/all/', response_model=list[schemas.DeviceListOut])
def get_all_device( db: Session = Depends(get_db), ):
    # print(f'id: {id}')
    # ----------------------
    Device_list = db.query(models.Device_list)
    # Device_list=Device_list.__dict__
    # ----------------------
    if not Device_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    
    return Device_list.all()

# Describe functions before writing code
# /**
# 	 * @description get device config
# 	 * @author vnguyen
# 	 * @since 01-12-2023
# 	 * @param {db}
# 	 * @return data (DeviceConfigOut)
# 	 */ 

@router.get('/config/', response_model=schemas.DeviceConfigOut)
def get_device_config( db: Session = Depends(get_db), ):
    # print(f'id: {id}')
    # ----------------------
    device_type_query = db.query(models.device_type)
    if not device_type_query.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device type does not exist")
    device_group_query = db.query(models.device_group)
    if not device_group_query.all():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device group does not exist")
    device_list_query = db.query(models.Device_list).order_by(models.Device_list.id.asc())
    communication_query = db.query(models.Communication)
    result_device_type=[]
    for item in device_type_query.all():
        result_device_type.append(item.__dict__)
    result_device_group=[]
    for item in device_group_query.all():
        new_item=item.__dict__
        new_item["template"]=item.template.__dict__
        result_device_group.append(new_item) 
    result_device_list=[]
    for item in device_list_query.all():
        result_device_list.append(item.__dict__)
    result_communication=[]
    for item in communication_query.all():
        new_item=item.__dict__
        new_item["driver_list"]=item.driver_list.__dict__
        result_communication.append(new_item) 
        

    # https://docs.sqlalchemy.org/en/14/core/tutorial.html#using-textual-sql
 
    return {
        "device_list":result_device_list,
        "device_type":result_device_type,
        "device_group":result_device_group,
        "communication":result_communication
    }
# Describe functions before writing code
# /**
# 	 * @description create device
# 	 * @author vnguyen
# 	 * @since 01-12-2023
# 	 * @param {DeviceCreate,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/create/", response_model=schemas.DeviceState)
async def create_device(create_device: schemas.DeviceCreate,db: Session = Depends(get_db)):
    
    # create_device: list[schemas.DeviceCreate],
    try:
        # format id =
        # create table
        async def execute_func():
            try:
                # {                 
                    # "name": "UNO-DM-3.3-TL-PLUS",
                    # "device_virtual": False,
                    # "id_communication": 3,
                    
                    # "id": 7,
                    # "rtu_bus_address": 2,
                    # "tcp_gateway_port": 502,
                    # "tcp_gateway_ip": "192.168.80.101",
                    # "id_device_type": 1,
                    # "connect_type":"Modbus/TCP",
                    # "id_device_group": 1
                # }
                # DROP TABLE dev_007;
                # DELETE FROM `device_list` WHERE id=7;
                # SELECT *FROM device_list;
                # DELETE FROM `device_register_block` WHERE id_device_list=7;
                # DELETE FROM `device_point_list` WHERE id_device_list=7;
                # {
                        # "id": 6,
                        # "name": "MFM383A-4",
                        # "device_virtual": false,
                        # "id_device_type": 3,
                        # "id_communication": 2,
                        # "connect_type":"RS485",
                        # "id_device_group":3,      
                        
                        # "rtu_bus_address": 3,
                        # "tcp_gateway_port": 502,
                        # "tcp_gateway_ip": ""
                        
                        
                # }
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
                    new_device = models.Device_list(pv=pv,
                                                    model=model,
                                                    send_p=send_p,
                                                    send_q=send_q,
                                                    send_pf=send_pf,
                                                    value_pf=value_pf,
                                                    max=max,
                                                    enable_poweroff=enable_poweroff,
                                                    **create_device.dict())
                    
                    db.add(new_device)
                    db.commit()
                    db.refresh(new_device)
                    # insert success new device
                    if not new_device:
                        return 200    
                    # read file mybatis query sql
                    id=create_device.id
                    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/device.xml')
                    statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
                        
                    sql_query=statement[0]["create_device"]
                    sql_register_block=statement[1]["insert_device_register_block"]
                    sql_point_list=statement[2]["insert_device_point_list"]
                    sql_select_device=statement[4]["select_all_device"]
                
                    sql = sql_query.replace("table_name", f'dev_{str(id).zfill(3)}')
                    # create table new device
                    result_create_table = db.execute(text(sql))
                    print(result_create_table.__dict__)
                    if 'rowcount' in result_create_table.__dict__.keys():             
                        communication_query = db.query(models.Communication).filter(models.Communication.id == create_device.id_communication).first()
                        print(communication_query.__dict__)
                        if not communication_query:
                            return 200                   
                        if not communication_query.driver_list:
                            return 200 
                       
                        driver_list=communication_query.driver_list
                        # check TCP/RS485
                        if driver_list.name=="RS485":
                            # insert device_register_block
                            result_register_block = db.execute(text(sql_register_block), params={'id': id})
                            db.commit()
                            print(f'result_register_block: {result_register_block.__dict__}')
                            if not 'rowcount' in result_register_block.__dict__.keys():
                              return 200
                            # insert device_point_list
                            result_point_list = db.execute(text(sql_point_list), params={'id': id})
                            db.commit()
                            print(f'result_point_list: {result_point_list.__dict__}')
                            if not 'rowcount' in result_point_list.__dict__.keys():
                              return 200
                            # check list device and Exclusions device new
                            device_list_query = db.query(
                                models.Device_list).filter(models.Device_list.id != 
                                                            create_device.id).order_by(
                                                            models.Device_list.id.asc()).all()
                           
                            if device_list_query:
                                # check device same group rs485 com port   
                                item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                            create_device.id_communication]
                                # find device in group rs485
                                if item_rs485:
                                    print('---------- Re-initialize group RS485 same com port ----------')
                                    # delete pm2 app rs485 running                       
                                    result_delete_app_pm2=delete_program_pm2(f'Dev|{str(create_device.id_communication)}|')
                                    # delete success app pm2
                                    if result_delete_app_pm2!=100:
                                        return 200
                                    # check group rs485 same com port
                                    result_device_group_rs485 = db.execute(
                                                                            text(sql_select_device), 
                                                                            params={'id_communication': 
                                                                            create_device.id_communication}).all()
                                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                                    if results_device_group_dict:
                                        # init restart pm2 app same rs485
                                        create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                        return 100
                                    else:
                                        return 200                                     
                                else:
                                    print('---------- create group RS485 same com port ----------')
                                    # init start pm2 new app
                                    # check group rs485 same com port
                                    result_device_group_rs485 = db.execute(
                                                                            text(sql_select_device), 
                                                                            params={'id_communication': 
                                                                            create_device.id_communication}).all()
                                    results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                                    if results_device_group_dict:
                                        # init restart pm2 app same rs485
                                        create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                        return 100
                                    else:
                                        return 200  
                                
                            else:
                                print('---------- create group RS485 same com port when list device empty ----------')
                                # check group rs485 same com port 
                                result_device_group_rs485 = db.execute(
                                                                            text(sql_select_device), 
                                                                            params={'id_communication': 
                                                                            create_device.id_communication}).all()
                                results_device_group_dict = [row._asdict() for row in result_device_group_rs485]                                                        
                                if results_device_group_dict:
                                    # init restart pm2 app same rs485
                                    create_device_group_rs485_run_pm2(path,results_device_group_dict)
                                    return 100
                                else:
                                    return 200  
                                                                                      
                        elif driver_list.name=="Modbus/TCP":
                            print(driver_list.name)
                            # insert device_register_block
                            result_register_block = db.execute(text(sql_register_block), params={'id': id})
                            db.commit()
                            print(f'result_register_block: {result_register_block.__dict__}')
                            if not 'rowcount' in result_register_block.__dict__.keys():
                              return 200
                            # insert device_point_list
                            result_point_list = db.execute(text(sql_point_list), params={'id': id})
                            db.commit()
                            print(f'result_point_list: {result_point_list.__dict__}')
                            if not 'rowcount' in result_point_list.__dict__.keys():
                              return 200
                            # init start pm2 new app
                            id_communication=create_device.id_communication
                            id = create_device.id
                            name = create_device.name
                            connect_type=driver_list.name
                            pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                            create_program_pm2(f'{path}/driver_of_device/ModbusTCP.py',pid,id)
                            return 100
                        
                        else:
                            return 200
                         

                    
            except Exception as err:
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