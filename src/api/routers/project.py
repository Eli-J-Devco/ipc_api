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

# import models
# import oauth2
import psutil
# import schemas
import serial.tools.list_ports as ports
from async_timeout import timeout
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
# from api.domain.project import models, schemas
import api.domain.project.models as project_models
import api.domain.project.schemas as project_schemas
import model.models as models
import utils.oauth2 as oauth2
from database.db import engine, get_db

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
@router.post('/', response_model= project_schemas.ProjectOut)
def get_project(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    try:
        # ----------------------
        project_query = db.query( project_models.Project_setup).filter( project_models.Project_setup.id == id).first()
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
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")
# Describe functions before writing code
# /**
# 	 * @description update project logging rate
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectLoggingRateUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_logging_rate/', response_model= project_schemas.ProjectState)
def update_project_logging_rate(id: int,
                                updated_logging_rate:  project_schemas.ProjectLoggingRateUpdate, 
                                db: Session = Depends(get_db),
                                current_user: int = Depends(oauth2.get_current_user)
                                ):
    try:
        # ----------------------
        print(updated_logging_rate)
        project_query = db.query( project_models.Project_setup).filter( project_models.Project_setup.id == id)
    

        if not project_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Project with id: {id} does not exist")
        project_query.update(updated_logging_rate.dict(), synchronize_session=False)
        db.commit()
        return {"status": "success","code": "200"}
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")
# Describe functions before writing code
# /**
# 	 * @description update project remote access
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectRemoteAccessUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_remote_access/', response_model= project_schemas.ProjectState)
def update_project_remote_access(id: int,
                                 updated_remote_access:  project_schemas.ProjectRemoteAccessUpdate, 
                                 db: Session = Depends(get_db),
                                 current_user: int = Depends(oauth2.get_current_user)
                                 ):
    try:
        # ----------------------
        
        project_query = db.query( project_models.Project_setup).filter( project_models.Project_setup.id == id)
    

        if not project_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Project with id: {id} does not exist")
        project_query.update(updated_remote_access.dict(), synchronize_session=False)
        db.commit()
        return {"status": "success","code": "200"}
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")
# Describe functions before writing code
# /**
# 	 * @description update project first page login
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,ProjectPageLoginUpdate,db}
# 	 * @return data (ProjectState)
# 	 */
@router.post('/update_first_page_login/', response_model= project_schemas.ProjectState)
def update_project_first_page_login(id: int,
                                    updated_page_login:  project_schemas.ProjectPageLoginUpdate, 
                                    db: Session = Depends(get_db),
                                    current_user: int = Depends(oauth2.get_current_user)
                                    ):
    try:
        # ----------------------
        
        project_query = db.query( project_models.Project_setup).filter( project_models.Project_setup.id == id)
        

        if not project_query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Project with id: {id} does not exist")
        project_query.update(updated_page_login.dict(), synchronize_session=False)
        db.commit()
        return {"status": "success","code": "200"}
    except (Exception) as err:
        print('Error : ',err)
        raise HTTPException(status_code=500, detail="Internal server error")