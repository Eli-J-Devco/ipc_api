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
from model.schemas import type_logging_interval


# <- project ->
class PageBase(BaseModel):
    id : Optional[int] = None
    name : Optional[str] = None
    description : Optional[str] = None
    class Config:
        orm_mode = True

class ProjectBase(BaseModel):

    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None
    
    id_first_page_on_login: Optional[int] = None
    id_logging_interval: Optional[int] = None
    id_scheduled_upload_time: Optional[int] = None
    number_times_retry: Optional[int] = None
    id_time_wait_before_retry: Optional[int] = None
    id_upload_debug_information: Optional[int] = None
    enable_upload_data_on_alarm_status: Optional[bool] = None
    enable_upload_data_on_low_disk: Optional[bool] = None
    enable_upload_data_on_system_startup: Optional[bool] = None
    
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None
    
    id_time_zone : Optional[int] = None
    Time1cycle : Optional[float] = None
    sampling_time1cycle : Optional[float] = None

    enable_zero_export : Optional[bool] = None
    value_zero_export : Optional[float] = None

    enable_limit_energy : Optional[bool] = None
    value_limit_energy : Optional[float] = None
    
    modhopper1 : Optional[int] = None
    modhopper2 : Optional[int] = None
    modhopper_key : Optional[str] = None
    modhopper_rf_config : Optional[int] = None
    modhopper_rf_channel : Optional[int] = None
    status : Optional[bool] = None
    logging_interval:type_logging_interval
    logging_interval_list:list[type_logging_interval]
    first_page_on_login:PageBase
    page_list:list[PageBase]
    class Config:
        orm_mode = True
class ProjectOut(ProjectBase):
    id: Optional[int] = None
   
    class Config:
        orm_mode = True
class ProjectCreate(ProjectBase):
    pass
class ProjectUpdate(ProjectBase):
    pass

class ProjectRemoteAccessUpdate(BaseModel):
    link_remote_access: Optional[str] = None
    allow_remote_access: Optional[bool] = None
    class Config:
        orm_mode = True
class ProjectLoggingRateUpdate(BaseModel):
    id_logging_interval: Optional[int] = None
    class Config:
        orm_mode = True
class ProjectPageLoginUpdate(BaseModel):
    id_first_page_on_login: Optional[int] = None
    class Config:
        orm_mode = True
class ProjectSearchModBusUpdate(BaseModel):
    # enable_search_modbus_rtu_device: Optional[int] = None
    enable_search_modbus_rtu_device: bool = Field(..., alias='search_modbus_rtu_device')
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class ProjectState(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True