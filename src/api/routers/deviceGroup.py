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
from async_timeout import timeout
from fastapi import (APIRouter, Body, Depends, FastAPI, HTTPException, Query,
                     Response, status)
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc
from sqlalchemy.orm import Session
from sqlalchemy.sql import func, insert, join, literal_column, select, text

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
# from utils.logger_manager import setup_logger

import utils.oauth2 as oauth2
# LOGGER = setup_logger(module_name='API')
from api.domain.deviceGroup import models, schemas
from database.db import engine, get_db
from utils.pm2Manager import (create_device_group_rs485_run_pm2,
                              create_program_pm2, delete_program_pm2,
                              find_program_pm2, restart_pm2_change_template,
                              restart_program_pm2, restart_program_pm2_many)

router = APIRouter(
    prefix="/device_group",
    tags=['Device_group']
)
# Describe functions before writing code
# /**
# 	 * @description get device group
# 	 * @author vnguyen
# 	 * @since 09-01-2024
# 	 * @param {db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/get_all/', response_model=list[schemas.DeviceGroupOutBase])
def get_all_group( db: Session = Depends(get_db) ,  current_user: int = Depends(oauth2.get_current_user)):
    try:
        
        device_group_query = db.query(models.Device_group).filter(
        models.Device_group.status == 1)
        result_device_group=device_group_query.all()
        if not result_device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Not have Device group")
        return result_device_group
        
    except Exception as err: 
        print('Error : ',err)
        # LOGGER.error(f'--- {err} ---')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")

# Describe functions before writing code
# /**
# 	 * @description get device group
# 	 * @author vnguyen
# 	 * @since 09-01-2024
# 	 * @param {db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/get_each/', response_model=schemas.DeviceGroupOutBase)
def get_each_group(id_device_group: Optional[int] = Body(embed=True), db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user) ):
    try:
        
        device_group_query = db.query(models.Device_group).filter(
        models.Device_group.id == id_device_group).filter(
        models.Device_group.status == 1)
        result_device_group=device_group_query.first()
        if not result_device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Not have Device group")
        # 
        template_query = db.query(models.Template_library).filter(
        models.Device_group.status == 1)
        result_template=template_query.all()
        if not result_template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Not have template")
        # 
        template_list=[item.__dict__ for item in result_template]
       
        result={
           **result_device_group.__dict__,
           "template_list":template_list
           
        }
        return result
    except Exception as err: 
        print('Error : ',err)
        # LOGGER.error(f'--- {err} ---')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description edit group device
# 	 * @author vnguyen
# 	 * @since 09-01-2024
# 	 * @param {device_group,db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/edit_each/', response_model=schemas.DeviceGroupOutBase)
def edit_each_group(device_group: schemas.DeviceGroupBase,db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user) ):
    try:
        id=device_group.id
        device_group_query = db.query(models.Device_group).filter(
        models.Device_group.id == id)
        result_device_group=device_group_query.first()
        if not result_device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Device group with id: {id} does not exist")
        
        device_group_query.update(device_group.dict())
        print(f'id_template: {result_device_group.id_template}')
        if result_device_group.id_template:
            id_template=result_device_group.id_template
            restart_pm2_change_template(id_template,db)
        db.commit()
        return result_device_group
    except exc.SQLAlchemyError as err:
        print('Error : ',err)
        # LOGGER.error(f'--- {err} ---')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description create group device
# 	 * @author vnguyen
# 	 * @since 09-01-2024
# 	 * @param {device_group,db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/create/', response_model=schemas.DeviceGroupOutBase)
def create_group(device_group: schemas.DeviceGroupCreateBase,db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user) ):
    try:
        name=device_group.name
        device_group_query = db.query(models.Device_group).filter(
        models.Device_group.name == name).all()
        if device_group_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Group name already exists")
        
        new_device_group = models.Device_group(**device_group.dict())
        db.add(new_device_group)
        db.commit()
        db.refresh(new_device_group)
        
        return new_device_group
    except exc.SQLAlchemyError as err:
        print('Error : ',err)
        # LOGGER.error(f'--- {err} ---')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")
# Describe functions before writing code
# /**
# 	 * @description create group device
# 	 * @author vnguyen
# 	 * @since 09-01-2024
# 	 * @param {device_group,db}
# 	 * @return data (DeviceGroupOutBase)
# 	 */
@router.post('/delete_group/', response_model=schemas.DeviceGroupStateBase)
def delete_group(device_group: schemas.DeviceGroupBase,db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user) ):
    try:
        id=device_group.id
        device_group_query = db.query(models.Device_group).filter(models.Device_group.id == id)
        result_device_group=device_group_query.first()
        
        if not result_device_group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Device group with id: {id} does not exist")
        
        device_group_query.filter(models.Device_group.id == id).delete(synchronize_session=False)
        print(f'id_template: {result_device_group.id_template}')
        if result_device_group.id_template:
            id_template=result_device_group.id_template
            restart_pm2_change_template(id_template,db)
        db.commit()
        return {
                "status": "success",
                "code": "100",
                "desc":""
            }
    except exc.SQLAlchemyError as err:
        print('Error : ',err)
        # LOGGER.error(f'--- {err} ---')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")