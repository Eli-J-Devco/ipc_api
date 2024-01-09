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
from sqlalchemy.sql import func, insert, join, literal_column, select, text
from utils import (create_device_group_rs485_run_pm2, create_program_pm2,
                   delete_program_pm2, find_program_pm2, get_mybatis, path,
                   restart_pm2_change_template, restart_program_pm2,
                   restart_program_pm2_many)

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
@router.post('/get_device_group/', response_model=list[schemas.DeviceGroupOutBase])
def get_device_group( db: Session = Depends(get_db) ):
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
@router.post('/get_each_group_device/', response_model=schemas.DeviceGroupOutBase)
def get_each_device_group(id_device_group: Optional[int] = Body(embed=True), db: Session = Depends(get_db) ):
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
@router.post('/edit_each_device_group/', response_model=schemas.DeviceGroupOutBase)
def edit_each_device_group(device_group: schemas.DeviceGroupBase,db: Session = Depends(get_db) ):
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
@router.post('/create_device_group/', response_model=schemas.DeviceGroupOutBase)
def create_device_group(device_group: schemas.DeviceGroupCreateBase,db: Session = Depends(get_db) ):
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
@router.post('/delete_device_group/', response_model=schemas.DeviceGroupStateBase)
def delete_device_group(device_group: schemas.DeviceGroupBase,db: Session = Depends(get_db) ):
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Not have data")