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
from database import get_db
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from config import Config

# 
router = APIRouter(
    prefix="/rs485",
    tags=['RS485']
)
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
    result_communication,result_driver_list = db.query(models.Communication,models.Driver_list).join(
        models.Driver_list, models.Driver_list.id == models.Communication.id_driver_list, 
        isouter=True).group_by(models.Communication.id,models.Driver_list.id).filter(models.Communication.id == id).first()
    
   
    
   
    # 
    # p = schemas.BaudRate(**{'id': "1", 'name': '9600'})
    # 
    {
        "baud":[{"id":136,"namekey":"9600"},{"id":137,"namekey":"19200"}],
        "parity":[],
        "stop_bits":[],
        "timeout":[],
        "debuglevel":[]
    }
    # 
    # result_3=schemas.BaudRate(**communication_baud.__dict__).dict(by_alias=False)
    # print(f'baud :{baud}')
    # print(f'result_communication :{result_1}')
    # print(f'result_driver_list :{result_2}')
    # print(f'communication_baud :{result_3}')
    if not communication:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return communication
@router.post('/config', response_model=schemas.ConfigRS485Base)
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
@router.post('/serial')
def get_scan_serial():
    
    result=[]
    com_ports = list(ports.comports()) # create a list of com ['COM1','COM2'] 
    for i in com_ports:            
        result.append(i.device) # returns 'COMx
    print(result)
    return result
@router.post("/update/{id}", response_model=schemas.CommunicationOut)
async def update_rs485(id: int,  updated_communication: schemas.CommunicationCreate,db: Session = Depends(get_db)):
    try:
        communication_query = db.query(models.Communication).filter(models.Communication.id == id)
       
        if communication_query.first() == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"RS485 with id: {id} does not exist")
        communication_list=communication_query.first().__dict__
        # print(f'communication_list :{communication_list}')
       
        
        # communication_query.update(updated_communication.dict(), synchronize_session=False)
        # db.commit()
        shellscript = subprocess.Popen(["pm2", "jlist"],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
        print("------------------------------")
        # data = json.loads(raw)status
        out, err = shellscript.communicate()
        result = json.loads(out)
        # print(result)
        # for item in range(len(result)):
        #     print("+++++++++++++++++++++++++++++")

        #     name = result[item]['name']
        #     namespace = result[item]['pm2_env']['namespace']
        #     mode = result[item]['pm2_env']['exec_mode']
        #     pid = result[item]['pid']
        #     uptime = result[item]['pm2_env']['pm_uptime']
        #     status = result[item]['pm2_env']['status']
        #     cpu = result[item]['monit']['cpu']
        #     mem = result[item]['monit']['memory'] / 1000000

        #     print(f'name: {name}')
        #     print(f'namespace: {namespace}')
        #     print(f'mode: {mode}')
        #     print(f'pid: {pid}')
        #     print(f'uptime: {uptime}')
        #     print(f'status: {status}')
        #     print(f'cpu: {cpu}')
        #     print(f'mem: {mem}')
        return communication_query.first()
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Request timeout")