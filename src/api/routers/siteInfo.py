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

sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
import utils.oauth2 as oauth2
from api.domain.project import models as project_models
from api.domain.siteInfo import schemas
from database.db import engine, get_db

# from config import Config

# 
router = APIRouter(
    prefix="/site_information",
    tags=['SiteInformation']
)
# Describe functions before writing code
# /**
# 	 * @description get site information
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (SiteInformOut)
# 	 */
@router.post('/', response_model=schemas.SiteInformOut)
def get_site_information(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user) ):
    try:
        
        print('------------------------------------------')
        print(f'{id}')
        # ----------------------
        site_information_query = db.query(project_models.Project_setup).filter(project_models.Project_setup.id == int(id)).first()
        print(site_information_query)
        print('+++++++++++++++++++++++++++++++')
        if not site_information_query:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Site information with id: {id} does not exist")

        return site_information_query
    except (Exception) as err:
        print(err)
# Describe functions before writing code
# /**
# 	 * @description update site information
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,updated_SiteInform,db}
# 	 * @return data (SiteInformOut)
# 	 */
@router.post("/update/", response_model=schemas.SiteInformOut)
def update_site_information(id: int,  updated_SiteInform: schemas.SiteInformUpdate,db: Session = Depends(get_db),  current_user: int = Depends(oauth2.get_current_user)):
    
    
    site_information_query = db.query(project_models.Project_setup).filter(project_models.Project_setup.id == id)
    if site_information_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Site information with id: {id} does not exist")
    site_information_query.update(updated_SiteInform.dict(), synchronize_session=False)
    db.commit()
    return site_information_query.first()
# 

