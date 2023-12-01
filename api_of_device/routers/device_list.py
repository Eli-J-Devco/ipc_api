# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime

import models
import mybatis_mapper2sql
import oauth2
import schemas
import utils
from async_timeout import timeout
from database import get_db
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from utils import path, restart_program_pm2

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
# 	 * @since 30-11-2023
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
        # result_communication.append(item.__dict__)
        
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
                    # "device_virtual": false,
                    # "id_communication": 3,
                    # "id": 7,
                    # "rtu_bus_address": 1,
                    # "tcp_gateway_port": 502,
                    # "tcp_gateway_ip": "192.168.80.101",
                    # "id_device_type": 1,
                    # "connect_type":"Modbus/TCP",
                    # "id_device_group": 1
                # }
                # create table new device
                id=create_device.id
                mapper, xml_raw_text = mybatis_mapper2sql.create_mapper(xml=path+'/mybatis/device.xml')
                statement = mybatis_mapper2sql.get_statement(
                mapper, result_type='list', reindent=True, strip_comments=True)
                sql_query=statement[1]["select_upload_channel"]
                sql = sql_query.replace("table_name", f'dev_{str(id).zfill(3)}')
                result_create_table = db.execute(text(sql))
                # insert new device to table
                if 'rowcount' in result_create_table.__dict__.keys():             
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
                    if new_device:
                        print(new_device)
                        # check TCP/RS485
                    
            except Exception as err:
                print('Error create table : ',err)
                return 300
        async with timeout(5) as cm:
            response=  await execute_func() 
            if response==100:    
                return {"status": "success","code": str(response)}
            elif response==200:
                return {"status": "success","code": str(response)}
            elif response==300:
                return {"status": "success","code": str(response)}
            else:
                return {"status": "success","code": "400"}
        
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")