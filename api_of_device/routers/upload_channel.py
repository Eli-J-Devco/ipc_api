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

from config import Config

# 
router = APIRouter(
    prefix="/upload_channel",
    tags=['UploadChannel']
)

@router.post("/all_channel/", response_model=schemas.UploadChannelOut)
def get_upload_channel(db: Session = Depends(get_db)):
    try:
        upload_channel_query = db.query(models.Upload_channel).filter(models.Upload_channel.status == 1)
        result=upload_channel_query.all()
        
        # print(result[0].__dict__)
        # print(result[0].type_protocol.__dict__)

        Channel_list=[]
        for item in result:
            new_item=item.__dict__
            print(f'new_item1: {new_item}')
            new_item["type_protocol"]=item.type_protocol.__dict__
            print(f'new_item2: {new_item}')
            Channel_list.append(
                new_item
            )
        print(f'Channel_list: {Channel_list}')
         
        
        all_channel = [item.__dict__ for item in upload_channel_query]
        # print(all_channel[0])
        return upload_channel_query.first()
        # return {
        #     "all_channel":all_channel
        # }
    except Exception as err:
        pass
        # print(f"Error : '{err}'")
# @router.post("/update/{id}", response_model=schemas.UploadChannelOut)
# async def update_upload_channel(id: int,  updated_communication: schemas.CommunicationCreate,db: Session = Depends(get_db)):
#     try:
#         upload_channel_query = db.query(models.Upload_channel).filter(models.Upload_channel.status == 1)
#         return upload_channel_query.first()
#     except asyncio.TimeoutError:
#         raise HTTPException(status_code=408, detail="Request timeout")