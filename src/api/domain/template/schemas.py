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
# from api.domain.deviceGroup.schemas import DeviceGroupBase
from model.schemas import (DataTypeBase, PointByteOrder, PointDataType,
                           PointOutBase, PointUnit, RegisterListBase,
                           TypeByteOrderBase, TypeClassBase, TypePointBase,
                           TypeUnitsBase)


# <- template_library ->
class TemplateBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    
    class Config:
        orm_mode = True
# <-  -> 

class TemplateCreateBase(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None
    id_template_type:Optional[int] = None
    class Config:
        orm_mode = True
class TemplateOutBase(TemplateCreateBase):
    id: Optional[int] = None
    # name: Optional[str] = None
    # status: Optional[bool] = None
    # point_list : list[PointOutBase]
    class Config:
        orm_mode = True
class TemplateUpdateBase(TemplateCreateBase):
    id: Optional[int] = None
    class Config:
        orm_mode = True        
class TemplateTypeBase(BaseModel):
    id: Optional[int] = Field(..., alias='id')
    namekey: Optional[str] = Field(..., alias='types')
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True

    # id: Optional[int] = None
    # class Config:
    #     orm_mode = True        
class TemplateDelete(BaseModel):
    status: Optional[str] = None
    code: Optional[str] = None
    desc: Optional[str] = None
    
    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
# <-  ->       
class PointTemplateOutBase(PointOutBase):
    type_units_list: Optional[list[TypeUnitsBase]] = None
    type_datatype_list: Optional[list[DataTypeBase]] = None
    type_byteorder_list: Optional[list[TypeByteOrderBase]] = None
    
    type_point_list: Optional[list[TypePointBase]] = None
    type_class_list: Optional[list[TypeClassBase]] = None
    class Config:
        orm_mode = True
class TemplateListBase(BaseModel):
    data_type:list[PointDataType]=None
    byte_order:list[PointByteOrder]=None
    point_unit:list[PointUnit]=None
    point_list : list[PointOutBase]=None
    register_list : list[RegisterListBase]=None
    
    class Config:
        orm_mode = True
class PointInfoTemplateBase(BaseModel):
    id_point: Optional[int]=None

class PointDeleteTemplateBase(BaseModel):
    id_template: Optional[int]=None
    id_point:Optional[list[int]]=None
    
    class Config:
        orm_mode = True
        from_attributes = True