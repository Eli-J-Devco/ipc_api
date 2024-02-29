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
from api.domain.template.schemas import TemplateBase
from model.schemas import (PointByteOrder, PointDataType, PointOutBase,
                           PointUnit, RegisterListBase)


class DeviceGroupCreateBase(BaseModel):
    name: Optional[str] = None
    # status: Optional[bool] = None
    id_template: Optional[int] = None
    class Config:
        orm_mode = True
class DeviceGroupBase(DeviceGroupCreateBase):
    id: Optional[int] = None 
    # name: Optional[str] = None
    # status: Optional[bool] = None
    # id_template: Optional[int] = None
    # templates_library: TemplateOutBase
    
    class Config:
        validate_assignment = True
    # @validator("id", pre=True, always=True)
    # def _encryption_id(cls, id: str):
    #     id_hash=str(id)
    #     return sha256(id_hash.encode('utf-8')).hexdigest()
class DeviceGroupStateBase(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    class Config:
        orm_mode = True
class DeviceGroupOutBase(BaseModel):
    id: Optional[int] = None 
    name: Optional[str] = None
    status: Optional[bool] = None
    id_template: Optional[int] = None
    # templates_library: TemplateOutBase
    template_list:Optional[list[TemplateBase]] = None 
    class Config:
        orm_mode = True
class TemplateGroupDeviceOutBase(BaseModel):
    device_group:DeviceGroupBase=None
    data_type:list[PointDataType]=None
    byte_order:list[PointByteOrder]=None
    point_unit:list[PointUnit]=None
    point_list : list[PointOutBase]=None
    register_list : list[RegisterListBase]=None
    
    class Config:
        orm_mode = True