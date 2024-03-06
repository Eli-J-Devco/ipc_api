# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import asyncio
import datetime
import json
import os
import subprocess
from pathlib import Path

import psutil
import serial.tools.list_ports as ports
from async_timeout import timeout
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

import api.domain.project.models as project_models
import api.domain.project.schemas as project_schemas
import api.domain.rs485.models as rs485_models
import api.domain.rs485.schemas as rs485_schemas
import model.models as models
import model.schemas as schemas
import utils.oauth2 as oauth2
from database.db import engine, get_db
from utils.pm2Manager import (delete_program_pm2, restart_program_pm2,
                              stop_program_pm2)

# 
router = APIRouter(
    prefix="/rs485",
    tags=['RS485']
)
# Describe functions before writing code
# /**
# 	 * @description get rs485
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (CommunicationOut)
# 	 */
@router.post('/', response_model=rs485_schemas.CommunicationOut)
def get_rs485(id: int, db: Session = Depends(get_db), 
              current_user: int = Depends(oauth2.get_current_user)):
    # ----------------------
    communication = db.query(models.Communication).filter_by(id =id).first()
    # ethernet_list=ethernet.__dict__
    # print(f'ethernet :{ethernet_list}')
    # ----------------------
    # result = db.execute(
    # text(f'select * from user')).all()
    # results_dict = [row._asdict() for row in result]
    # print(f'{results_dict}')
    # ----------------------
    # result_communication,result_driver_list = db.query(models.Communication,models.Driver_list).join(
    #     models.Driver_list, models.Driver_list.id == models.Communication.id_driver_list, 
    #     isouter=True).group_by(models.Communication.id,models.Driver_list.id).filter(models.Communication.id == id).first()
    

    

    if not communication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    
    communication_rs485 = db.query(models.Config_information).filter_by(id_type =4).filter_by(status = 1).all()
    if not communication_rs485:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    baud = [item.__dict__ for item in communication_rs485 if item.type == 401]
    parity= [item.__dict__ for item in communication_rs485 if item.type == 402]
    stop_bits= [item.__dict__ for item in communication_rs485 if item.type == 403]
    debuglevel= [item.__dict__ for item in communication_rs485 if item.type == 404]
    timeout= [item.__dict__ for item in communication_rs485 if item.type == 405]
    # 
    rs485Inf={
        "baud":baud, #id_type_baud_rates
        "parity":parity, #id_type_parity
        "stop_bits":stop_bits, #id_type_stopbits
        "debuglevel":debuglevel, #id_type_debug_level
        "timeout":timeout, #id_type_timeout
    }
    # print(result.driver_list.__dict__)
    # p = rs485_schemas.CommunicationOut(**{"rs485Inf": rs485Inf})
    # return p
    return {
            **communication.__dict__,
            **communication.driver_list.__dict__,
            "rs485Inf":rs485Inf
    }
# Describe functions before writing code
# /**
# 	 * @description get rs485 config
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {db}
# 	 * @return data (RS485ConfigBase)
# 	 */
@router.post('/config/', response_model=rs485_schemas.RS485ConfigBase)
# , response_model_by_alias=False
def get_rs485_config( db: Session = Depends(get_db), 
                     current_user: int = Depends(oauth2.get_current_user)):
    communication_rs485 = db.query(models.Config_information).filter_by(id_type =4).filter_by(status = 1).all()
    if not communication_rs485:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")
    baud = [item.__dict__ for item in communication_rs485 if item.type == 401]
    parity= [item.__dict__ for item in communication_rs485 if item.type == 402]
    stop_bits= [item.__dict__ for item in communication_rs485 if item.type == 403]
    debuglevel= [item.__dict__ for item in communication_rs485 if item.type == 404]
    timeout= [item.__dict__ for item in communication_rs485 if item.type == 405]
    # p = schemas.RS485BaudRate(**{'id': "1", 'namekey': '9600'})
    # print(f'p :{p}')
    
    return {
        "baud":baud,
        "parity":parity,
        "stop_bits":stop_bits,
        "debuglevel":debuglevel,
        "timeout":timeout,
    }
# Describe functions before writing code
# /**
# 	 * @description get scan serial
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {}
# 	 * @return data (SerialListBase)
# 	 */
@router.post('/serial/', response_model=rs485_schemas.SerialListBase)
def get_scan_serial(current_user: int = Depends(oauth2.get_current_user)):
    
    result=[]
    com_ports = list(ports.comports()) # create a list of com ['COM1','COM2'] 
    for i in com_ports:            
        result.append({"serial_port":i.device}) # returns 'COMx
    
    # {
    #     "serial_list":[{
    #         "serial_port":""
    #     }]
    # }
    
   
    return {"serial_list":result}
# Describe functions before writing code
# /**
# 	 * @description update rs485
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,CommunicationCreate,db}
# 	 * @return data (RS485State)
# 	 */   
@router.post("/update/{id}", response_model=rs485_schemas.RS485State)
async def update_rs485(id: int,  
                       updated_communication: rs485_schemas.CommunicationCreate,
                       db: Session = Depends(get_db),
                       current_user: int = Depends(oauth2.get_current_user)
                       ):
    try:
        communication_query = db.query(models.Communication).filter_by(id = id)
       
        if communication_query.first() == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"RS485 with id: {id} does not exist")
                      
        async def execute_func():
            try:       
                result=restart_program_pm2(f'Dev|{str(id)}|')
                return result
            except Exception as err:
                print('Error restart pm2 : ',err)
                return 300
        async with timeout(5) as cm:
            response=  await execute_func()
            # print(response)
            if response==100:
                communication_query.update(updated_communication.dict(), synchronize_session=False)
                db.commit()
                return {"status": "success","code": str(response)}
            elif response==200:
                communication_query.update(updated_communication.dict(), synchronize_session=False)
                db.commit()
                return {"status": "success","code": str(response)}
            elif response==300:
                communication_query.update(updated_communication.dict(), synchronize_session=False)
                db.commit()
                return {"status": "success","code": str(response)}
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")
# Describe functions before writing code
# /**
# 	 * @description update rs485 update_search_modbus_rtu
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectSearchModBusUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_search_modbus_rtu/', response_model=rs485_schemas.RS485State)
def update_option_rs485_search_modbus(id: int,
                                      updated_search_modbus: rs485_schemas.S485SearchModBusUpdate, 
                                      db: Session = Depends(get_db) ,
                                      current_user: int = Depends(oauth2.get_current_user)
                                      ):
    # ----------------------
    
    project_query = db.query(project_models.Project_setup).filter_by(id = id)
   

    if not project_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} does not exist")
    project_query.update(updated_search_modbus.dict(), synchronize_session=False)
    db.commit()
    return {"status": "success","code": "200"}