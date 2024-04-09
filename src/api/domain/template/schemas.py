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
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    computed_field,
    root_validator,
    validator,
)
from pydantic.types import conint

sys.path.append(
    (
        lambda project_name: (
            os.path.dirname(__file__)[
                : len(project_name) + os.path.dirname(__file__).find(project_name)
            ]
            if project_name and project_name in os.path.dirname(__file__)
            else -1
        )
    )("src")
)
# from api.domain.deviceGroup.schemas import DeviceGroupBase
from model.schemas import (
    DataTypeBase,
    PointByteOrder,
    PointDataType,
    PointOutBase,
    PointUnit,
    RegisterListBase,
    TypeByteOrderBase,
    TypeClassBase,
    TypeFunctionBase,
    TypePointBase,
    TypePointListBase,
    TypeUnitsBase,
    ManualPointBase,
    PointBase,
    TypeControlGroupBase,
)


# <- template_library ->
class MPPTSTRINGPANEL(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    id_pointkey: Optional[str] = None

    class Config:
        orm_mode = True


class MPPTSTRING(BaseModel):

    id: Optional[int] = None
    name: Optional[str] = None
    id_pointkey: Optional[str] = None
    panel: list[MPPTSTRINGPANEL] = None

    class Config:
        orm_mode = True


class MPPTBase(BaseModel):
    # String: list[MPPTSTRING] = None
    id: Optional[int] = None
    name: Optional[str] = None
    id_pointkey: Optional[str] = None
    string: list[MPPTSTRING] = None

    class Config:
        orm_mode = True


class PANELOutBase(PointOutBase):
    class Config:
        orm_mode = True


class STRINGOutBase(PointOutBase):
    children: list[PANELOutBase] = []

    class Config:
        orm_mode = True
        from_attributes = True


class MPPTOutBase(PointOutBase):
    children: list[STRINGOutBase] = []

    class Config:
        orm_mode = True
        from_attributes = True


class TemplateMPPTBase(BaseModel):
    id: Optional[int] = None
    mppt: Optional[list[MPPTBase]] = None

    class Config:
        orm_mode = True


class TemplateBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    id_device_group: Optional[int] = None
    type: Optional[int] = None

    class Config:
        orm_mode = True


# <-  ->


class TemplateCreateBase(BaseModel):
    name: Optional[str] = None
    status: Optional[bool] = None
    id_device_group: Optional[int] = None
    type: Optional[int] = None

    class Config:
        orm_mode = True


class TemplateOutBase(TemplateCreateBase):
    id: Optional[int] = None

    # name: Optional[str] = None
    # status: Optional[bool] = None
    # point_list : list[PointOutBase]
    class Config:
        orm_mode = True


class TemplateTypeBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    namekey: Optional[str] = Field(..., alias="types")

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
class ManualPointOutBase(BaseModel):
    manual_list: Optional[list[ManualPointBase]] = None

    class Config:
        orm_mode = True


class PointTemplateOutBase(PointOutBase):
    type_units_list: Optional[list[TypeUnitsBase]] = None
    type_datatype_list: Optional[list[DataTypeBase]] = None
    type_byteorder_list: Optional[list[TypeByteOrderBase]] = None

    type_point_list: Optional[list[TypePointBase]] = None
    type_class_list: Optional[list[TypeClassBase]] = None

    class Config:
        orm_mode = True


class TemplateConfigBase(BaseModel):
    data_type: list[PointDataType] = None
    byte_order: list[PointByteOrder] = None
    point_unit: list[PointUnit] = None
    type_point: list[TypePointBase] = None
    type_point_list: list[TypePointListBase] = None
    type_class: list[TypeClassBase] = None
    type_function: list[TypeFunctionBase] = None
    type_control_group: list[TypeControlGroupBase] = None

    class Config:
        orm_mode = True


class TemplateListBase(BaseModel):
    # data_type:list[PointDataType]=None
    # byte_order:list[PointByteOrder]=None
    # point_unit:list[PointUnit]=None
    point_list: Optional[list[PointOutBase]] = None
    mppt_list: Optional[list[MPPTOutBase]] = None
    register_list: Optional[list[RegisterListBase]] = None

    class Config:
        orm_mode = True


class TemplateUpdateBase(TemplateListBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class PointInfoTemplateBase(BaseModel):
    id_point: Optional[int] = None
    id_pointkey: Optional[str] = None


class PointDeleteTemplateBase(BaseModel):
    id_template: Optional[int] = None
    points: Optional[list[PointInfoTemplateBase]] = None

    class Config:
        orm_mode = True
        from_attributes = True


class MPPTPointInfoTemplateBase(BaseModel):
    id_point: Optional[int] = None
    id_pointkey: Optional[str] = None
    id_config_information: Optional[int] = None
    parent: Optional[int] = None


class MPPTPointDeleteTemplateBase(BaseModel):
    id_template: Optional[int] = None
    points: Optional[list[MPPTPointInfoTemplateBase]] = None

    class Config:
        orm_mode = True
        from_attributes = True
