# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import uuid
from datetime import datetime
from hashlib import sha256
from typing import List, Optional

# 
from fastapi import APIRouter, Depends, Query
from pydantic import (BaseModel, EmailStr, Field, computed_field,
                      root_validator, validator)
from pydantic.types import conint

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from api.domain.deviceList.schemas import DeviceListBase
from model.schemas import type_logging_interval, type_protocol


class UploadChannelBase(BaseModel):
    # id_project_setup: int
    name: Optional[str] = None
    id_type_protocol: Optional[int] = None
    uploadurl: Optional[str] = None
    password: Optional[str] = None
    selected_upload: Optional[str] = None
    id_type_logging_interval: Optional[int] = None
    enable: Optional[bool] = None
    allow_remote_configuration: Optional[bool] = None
    class Config:
        orm_mode = True 
class UploadChannelOut(UploadChannelBase):
    id: Optional[int] = None
    type_protocol: type_protocol
    type_logging_interval: type_logging_interval
    status: Optional[bool] = None
    class Config:
        orm_mode = True
class AllUploadChannelOut(BaseModel):
    all_channel: list[UploadChannelOut]
   
    class Config:
        orm_mode = True

class UploadChannelCreate(UploadChannelBase):
    class Config:
        orm_mode = True 
class UploadChannelConfig(BaseModel):
    device_list: list[DeviceListBase]
    type_protocol:list[type_protocol]
    type_logging_interval:list[type_logging_interval]
    class Config:
        orm_mode = True
# 
class UploadChannelUpdate(UploadChannelBase):
    # del UploadChannelBase.status 
    # id: int
    id: Optional[int] = None
    class Config:
        orm_mode = True 
class UploadChannelState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True