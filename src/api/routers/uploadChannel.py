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
import sys
from pathlib import Path

# import oauth2
import psutil
# import schemas
import serial.tools.list_ports as ports
from async_timeout import timeout
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# from test.config import Config

path = (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)("src")
sys.path.append(path)
import api.domain.deviceList.models as deviceList_models
import api.domain.deviceList.schemas as deviceList_schemas
import api.domain.uploadChannel.models as uploadChannel_models
import api.domain.uploadChannel.schemas as uploadChannel_schemas
import model.models as models
import utils.oauth2 as oauth2
from database.db import engine, get_db
from utils.pm2Manager import (delete_program_pm2, restart_program_pm2,
                              restart_program_pm2_many, stop_program_pm2,
                              stop_program_pm2_many)

# 
router = APIRouter(
    prefix="/upload_channel",
    tags=['UploadChannel']
)
# Describe functions before writing code
# /**
# 	 * @description get all upload channel
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {db}
# 	 * @return data (AllUploadChannelOut)
# 	 */
@router.post("/all_channel/", response_model=uploadChannel_schemas.AllUploadChannelOut)
def get_all_upload_channel(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    try:
        upload_channel_query = db.query(uploadChannel_models.Upload_channel).filter(uploadChannel_models.Upload_channel.status == 1)
        result=upload_channel_query.all()
        
        Channel_list=[]
        for item in result:
            new_item=item.__dict__
            new_item["type_protocol"]=item.type_protocol.__dict__
            new_item["type_logging_interval"]=item.type_logging_interval.__dict__
            Channel_list.append(
                new_item
            )
        return {
            "all_channel":Channel_list
        }
    except Exception as err:
        
        print(f"Error : '{err}'")
# Describe functions before writing code
# /**
# 	 * @description get upload channel config
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {db}
# 	 * @return data (UploadChannelConfig)
# 	 */
@router.post('/config/', response_model=uploadChannel_schemas.UploadChannelConfig)
def get_upload_channel_config( db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    try:
        config_information_query = db.query(models.Config_information)\
            .filter(models.Config_information.id_type >= 6)\
            .filter(models.Config_information.id_type <= 7)\
            .filter_by(status = 1).all()
        if not config_information_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Config upload channel does not exist")
        device_list_query = db.query(deviceList_models.Device_list).filter_by(status = 1).all()
        if not device_list_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"The list does not contain any devices")
        type_protocol=[]
        type_protocol = [item.__dict__ for item in config_information_query if item.id_type == 7]
        type_logging_interval=[]
        type_logging_interval = [item.__dict__ for item in config_information_query if item.id_type == 6]
        device_list=[]
        device_list=[item.__dict__ for item in device_list_query]
        print(f'type_protocol: {type_protocol}')
        return {
            "type_protocol":type_protocol,
            "device_list":device_list,
            "type_logging_interval":type_logging_interval
        }
    except Exception as err: 
        print(f"Error : '{err}'")
# Describe functions before writing code
# /**
# 	 * @description update upload channel
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {list[schemas.UploadChannelUpdate],db}
# 	 * @return data (UploadChannelState)
# 	 */
@router.post("/update/", response_model=uploadChannel_schemas.UploadChannelState)
async def update_upload_channel(updated_communication: list[uploadChannel_schemas.UploadChannelUpdate],
                                db: Session = Depends(get_db)
                                , current_user: int = Depends(oauth2.get_current_user)
                                ):
    try:
        
        
        async def execute_func():
            try:
                count_upload_channel=0
                for channel in updated_communication:       
                    upload_channel_query = db.query(uploadChannel_models.Upload_channel).filter(uploadChannel_models.Upload_channel.id == channel.id)
                    db_upload_channel = upload_channel_query.first()
                    if not db_upload_channel:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Channel with this id: {channel.id} found",
                        )
                    result=0
                    
                    # restart program log run pm2
                    if bool(channel.enable)== True:
                        # result=restart_program_pm2(f'Log|{str(channel.id)}|')
                        pm2_app_list=[f'LogFile|{str(channel.id)}|',f'UpData|{str(channel.id)}|']
                        result=restart_program_pm2_many(pm2_app_list)
                        # print(f'result: {result}')
                    # delete program log run pm2
                    else:
                        # result=stop_program_pm2(f'Log|{str(channel.id)}|')
                        pm2_app_list=[f'LogFile|{str(channel.id)}|',f'UpData|{str(channel.id)}|']
                        result=stop_program_pm2_many(pm2_app_list)
                    if result == 100:
                        update_data = channel.dict()
                        upload_channel_query.filter(uploadChannel_models.Upload_channel.id == channel.id).update(
                            update_data, synchronize_session=False
                        )
                        db.commit()
                        count_upload_channel +=1
                    else:
                        update_data = channel.dict()
                        upload_channel_query.filter(uploadChannel_models.Upload_channel.id == channel.id).update(
                            update_data, synchronize_session=False
                        )
                        db.commit()
                    
                    await asyncio.sleep(2)
                # 
                if count_upload_channel >=len(updated_communication):
                    return 100
                else:
                    return 200
                    
            except Exception as err:
                print('Error restart pm2 : ',err)
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