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

import models
import oauth2
import psutil
import schemas
import serial.tools.list_ports as ports
from async_timeout import timeout
from database import get_db
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from utils import restart_program_pm2

from config import Config

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
@router.get('/{id}', response_model=schemas.CommunicationOut)
def get_rs485(id: int, db: Session = Depends(get_db), ):
    # ----------------------
    communication = db.query(models.Communication).filter(models.Communication.id == id).first()
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

    return communication
# Describe functions before writing code
# /**
# 	 * @description get rs485 config
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {db}
# 	 * @return data (RS485ConfigBase)
# 	 */
@router.post('/config/', response_model=schemas.RS485ConfigBase)
# , response_model_by_alias=False
def get_rs485_config( db: Session = Depends(get_db), ):
    communication_rs485 = db.query(models.Config_information).filter(models.Config_information.id_type == 4).filter(models.Config_information.status == 1).all()
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
@router.post('/serial/', response_model=schemas.SerialListBase)
def get_scan_serial():
    
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
@router.post("/update/{id}", response_model=schemas.RS485State)
async def update_rs485(id: int,  updated_communication: schemas.CommunicationCreate,db: Session = Depends(get_db)):
    try:
        communication_query = db.query(models.Communication).filter(models.Communication.id == id)
       
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