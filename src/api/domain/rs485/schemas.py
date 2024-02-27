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

class RS485BaudRate(BaseModel):
    id: int = Field(..., alias='id')
    namekey: int = Field(...,examples=[9600],alias='baud')
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485Parity(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='parity')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485StopBits(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='stop_bits')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485debuglevel(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='debuglevel')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485Timeout(BaseModel):
    id: int = Field(..., alias='id')
    namekey: str = Field(..., alias='timeout')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
class RS485ConfigBase(BaseModel):
    baud:list[RS485BaudRate]
    parity:list[RS485Parity]
    stop_bits:list[RS485StopBits]
    debuglevel:list[RS485debuglevel]
    timeout:list[RS485Timeout]
    class Config:
        orm_mode = True
class SerialBase(BaseModel):
    serial_port:Optional[str] = None
    class Config:
        orm_mode = True
class SerialListBase(BaseModel):
    serial_list:list[SerialBase]
    class Config:
        orm_mode = True
class RS485State(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True
class RS485State(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    class Config:
        orm_mode = True
class S485SearchModBusUpdate(BaseModel):
    # enable_search_modbus_rtu_device: Optional[int] = None
    enable_search_modbus_rtu_device: bool = Field(..., alias='search_modbus_rtu_device')
    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True