# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import ipaddress
import json
from pprint import pprint
from typing import Annotated, Optional, Union

import models
import mybatis_mapper2sql
import oauth2
import schemas
import utils
from async_timeout import timeout
from database import get_db
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
                   delete_program_pm2, find_program_pm2, path,
                   restart_program_pm2)

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
                    db.flush()
                    print(new_device.__dict__)

                    
                    # read file mybatis query sql
                    mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/device.xml')
                    statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
                            
                    sql_query=statement[0]["create_device"]
                    sql_register_block=statement[1]["insert_device_register_block"]
                    sql_point_list=statement[2]["insert_device_point_list"]
                    sql_select_device=statement[4]["select_all_device"]
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
                        db.query(models.Device_list).filter_by(id=id).delete()
                        db.commit()
                        return 300
                    finally:
                        pass
                    if not id :
                        db.rollback()
                        db.query(models.Device_list).filter_by(id=id).delete()
                     
                        return 300        
                    communication_query = db.query(models.Communication).filter(models.Communication.id == id_communication).first()
                    try:                    
                        if communication_query:
                            pass        
                        if communication_query.driver_list:
                            pass
                    except Exception as err:
                        print(err)
                        db.query(models.Device_list).filter_by(id=id).delete()
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
                            db.query(models.Device_list).filter_by(id=id).delete()
                            db.execute(text(f'DROP TABLE {name_device}'))                          
                            return 300
                        db.commit()                          
                        result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')                     
                        
                        if result_find_app_pm2==100:
                            result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')
                            # delete success app pm2
                            if result_delete_app_pm2!=100:
                                db.query(models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))
                                return 200                          
                            # check list device and Exclusions device new
                            device_list_query = db.query(
                                models.Device_list).filter(models.Device_list.id_communication ==
                                                            id_communication).filter(
                                models.Device_list.status == 1).order_by(
                                                            models.Device_list.id.asc()).all()
                            # check device same group rs485 com port   
                            item_rs485 = [item.__dict__ for item in device_list_query if item.id_communication == 
                                        id_communication]
                            # find device in group rs485
                            if not item_rs485:
                                db.query(models.Device_list).filter_by(id=id).delete()
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
                                    db.query(models.Device_list).filter_by(id=id).delete()
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
                                db.query(models.Device_list).filter_by(id=id).delete()
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
                                db.query(models.Device_list).filter_by(id=id).delete()
                                db.execute(text(f'DROP TABLE {name_device}'))                                                                 
                                return 300 
                            db.commit()
                            # init start pm2 new app
                            name = new_device.name
                            connect_type=driver_list.name
                            pid = f'Dev|{id_communication}|{connect_type}|{id}|{name}'
                            create_program_pm2(f'{path}/driver_of_device/ModbusTCP.py',pid,id)
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
@router.post("/create_multiple/", response_model=schemas.DeviceState)
async def create_multiple_device(create_device: schemas.MultipleDeviceCreate ,db: Session = Depends(get_db)):
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
                        new_device = models.Device_list(pv=pv,
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
                mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/device.xml')
                statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
                # create table new device            
                sql_query=statement[0]["create_device"]
                sql_register_block=statement[1]["insert_device_register_block"]
                sql_point_list=statement[2]["insert_device_point_list"]
                sql_select_device=statement[4]["select_all_device"]
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
                                    models.Device_list).filter(models.Device_list.id_communication ==
                                                                id_communication).filter(
                                    models.Device_list.status == 1).order_by(
                                                                models.Device_list.id.asc()).all()
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
                            create_program_pm2(f'{path}/driver_of_device/ModbusTCP.py',pid,item.id)
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
# 	 * @return data (DevicePointListOut)
# 	 */
@router.get('/point_list/', response_model=schemas.DevicePointListOut)
def get_point_list_only_device(id: int, db: Session = Depends(get_db) ):
    
    # ----------------------
    device_point_list_query = db.query(models.Device_point_list).filter(
        models.Device_point_list.id_device_list == id).all()
    # 
    if not device_point_list_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Device with id: {id} does not exist")

    return {"point_list":device_point_list_query}
# Describe functions before writing code
# /**
# 	 * @description delete device
# 	 * @author vnguyen
# 	 * @since 04-12-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/delete/", response_model=schemas.DeviceState)
async def delete_device(id: int,db: Session = Depends(get_db)):
    try:
        device_list_query = db.query(models.Device_list).filter(
        models.Device_list.id == id).filter(
        models.Device_list.status == 1).first()
        result=device_list_query
        result_communication=None
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
            # delete device TCP ------
            
            connect_type=result_driver.name
            id=id
        
            # delete data in table device_list -----
            result_delete_device_list =db.query(models.Device_list).filter_by(id=id).delete()
            db.commit()
            print(f'device_list: {result_delete_device_list}')
            # delete app running in pm2
            result_pm2=delete_program_pm2(f'Dev|{id_communication}|{connect_type}|{id}')
            print(f'result_pm2: {result_pm2}')
            restart_program_pm2(f'Log')
            return {"status": "success","code": str(100)}
            
        elif result_driver.name == "RS485":
            mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/device.xml')
            statement = mybatis_mapper2sql.get_statement(
                    mapper, result_type='list', reindent=True, strip_comments=True)
                        
            sql_query=statement[0]["create_device"]
            sql_register_block=statement[1]["insert_device_register_block"]
            sql_point_list=statement[2]["insert_device_point_list"]
            sql_select_device=statement[4]["select_all_device"]
            # delete data in table device_list -----
            result_delete_device_list =db.query(models.Device_list).filter_by(id=id).delete()
            db.commit()
            print(f'device_list: {result_delete_device_list}')
            # 
            result_find_app_pm2=find_program_pm2(f'Dev|{str(id_communication)}|')
            if result_find_app_pm2==100:
                result_delete_app_pm2=delete_program_pm2(f'Dev|{str(id_communication)}|')
                if result_delete_app_pm2!=100:
                    return {"status": "error","code": str(300)}
                all_device_list_query = db.query(
                                models.Device_list).filter(models.Device_list.id_communication ==id_communication
                                                            ).filter(
                                models.Device_list.status == 1).order_by(
                                                            models.Device_list.id.asc()).all()
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
# 	 * @since 06-12-2023
# 	 * @param {DeviceUpdateBase,db}
# 	 * @return data (DeviceState)
# 	 */
@router.post("/update/", response_model=schemas.DeviceState)
async def update_device_basic(update_device: schemas.DeviceUpdateBase,db: Session = Depends(get_db)):
    try:
        # name --> allow change
        # id_project_setup --> allow change
        # device_virtual --> lock
        # id_device_type --> allow change
        # id_communication --> lock
        # id_device_group if change it
            # - delete all in table device_point_list
            # - delete all in table device_register_block
            # - init parameter in table device_point_list
            # - init parameter in table device_register_block
        # rtu_bus_address --> allow change
        # tcp_gateway_ip --> allow change
        # tcp_gateway_port --> allow change
        
        # --> init app in pm2
        
        
        
        pass
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
