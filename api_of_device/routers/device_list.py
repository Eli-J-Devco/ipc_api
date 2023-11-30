# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

import models
import oauth2
import schemas
import utils
from database import get_db
from fastapi import (APIRouter, Depends, FastAPI, HTTPException, Response,
                     status)
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

router = APIRouter(
    prefix="/device_list",
    tags=['DeviceList']
)

# /device_list/
# /device_list


# Describe functions before writing code
# /**
# 	 * @description get device list
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {id,db}
# 	 * @return data (DeviceListOut)
# 	 */ 

@router.get('/{id}', response_model=schemas.DeviceListOut)
def get_device_list(id: int, db: Session = Depends(get_db), ):
    # print(f'id: {id}')
    # ----------------------
    Device_list = db.query(models.Device_list).filter(models.Device_list.id == id).first()
    Device_list=Device_list.__dict__
    print(f'device_list :{Device_list}')
    # ----------------------
    # result = db.execute(
    # text(f'select * from user')).all()
    # results_dict = [row._asdict() for row in result]
    # print(f'{results_dict}')
    # ----------------------
    if not Device_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id: {id} does not exist")

    return Device_list

