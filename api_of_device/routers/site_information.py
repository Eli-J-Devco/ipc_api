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
@router.get('/{id}', response_model=schemas.SiteInformOut)
def get_site_information(id: int, db: Session = Depends(get_db), ):
    # ----------------------
    site_information_query = db.query(models.Site_information).filter(models.Site_information.id == id).first()
   

    if not site_information_query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Site information with id: {id} does not exist")

    return site_information_query
# Describe functions before writing code
# /**
# 	 * @description update site information
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,updated_SiteInform,db}
# 	 * @return data (SiteInformOut)
# 	 */
@router.post("/update/{id}", response_model=schemas.SiteInformOut)
def update_site_information(id: int,  updated_SiteInform: schemas.SiteInformUpdate,db: Session = Depends(get_db)):
    site_information_query = db.query(models.Site_information).filter(models.Site_information.id == id)
    if site_information_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Site information with id: {id} does not exist")
    site_information_query.update(updated_SiteInform.dict(), synchronize_session=False)
    db.commit()
    return site_information_query.first()
# 