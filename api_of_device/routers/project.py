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

router = APIRouter(
    prefix="/project",
    tags=['Project']
)

# Describe functions before writing code
# /**
# 	 * @description get site information
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (ProjectOut)
# 	 */
@router.post('/', response_model=schemas.ProjectOut)
def get_project(id: int, db: Session = Depends(get_db), ):
    # ----------------------
    project_query = db.query(models.Project_setup).filter(models.Project_setup.id == id).first()
    if not project_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} does not exist")
    config_information_query = db.query(models.Config_information).filter(models.Config_information.id_type== 6).filter(models.Config_information.status == 1).all()
    if not config_information_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Config project logging rate does not exist")
    page_query = db.query(models.Page).filter(models.Config_information.status == 1).all()
    if not page_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Page does not exist")
            
    project_query.logging_interval_list=config_information_query
    project_query.first_page_on_login_list=page_query
    return project_query
# Describe functions before writing code
# /**
# 	 * @description update project logging rate
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectLoggingRateUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_logging_rate/', response_model=schemas.ProjectState)
def update_project_logging_rate(id: int,updated_logging_rate: schemas.ProjectLoggingRateUpdate, db: Session = Depends(get_db) ):
    # ----------------------
    print(updated_logging_rate)
    project_query = db.query(models.Project_setup).filter(models.Project_setup.id == id)
   

    if not project_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} does not exist")
    project_query.update(updated_logging_rate.dict(), synchronize_session=False)
    db.commit()
    return {"status": "success","code": "200"}
# Describe functions before writing code
# /**
# 	 * @description update project remote access
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectRemoteAccessUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_remote_access/', response_model=schemas.ProjectState)
def update_project_remote_access(id: int,updated_remote_access: schemas.ProjectRemoteAccessUpdate, db: Session = Depends(get_db) ):
    # ----------------------
   
    project_query = db.query(models.Project_setup).filter(models.Project_setup.id == id)
   

    if not project_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} does not exist")
    project_query.update(updated_remote_access.dict(), synchronize_session=False)
    db.commit()
    return {"status": "success","code": "200"}
# Describe functions before writing code
# /**
# 	 * @description update project first page login
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectPageLoginUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_first_page_login/', response_model=schemas.ProjectState)
def update_project_first_page_login(id: int,updated_page_login: schemas.ProjectPageLoginUpdate, db: Session = Depends(get_db) ):
    # ----------------------
    
    project_query = db.query(models.Project_setup).filter(models.Project_setup.id == id)
   

    if not project_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Project with id: {id} does not exist")
    project_query.update(updated_page_login.dict(), synchronize_session=False)
    db.commit()
    return {"status": "success","code": "200"}