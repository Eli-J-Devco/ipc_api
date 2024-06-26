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

# from api.domain.deviceList.schemas import DeviceListBase, DeviceListOut

# from model.schemas import (PointBase, PointByteOrder, PointDataType,
#                            PointOutBase, PointUnit, RegisterListBase)
# import api.domain.deviceList.schemas as deviceList_schemas

# ----------------------------------------------------


class type_protocol(BaseModel):
    id: int = Field(..., alias="id")
    namekey: str = Field(..., alias="Protocol")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


# <- Config_information ->
class ConfigInformationBase(BaseModel):
    # id : int
    parent: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    value: Optional[int] = None
    type: Optional[int] = None
    id_type: Optional[int] = None


class ConfigInformationOut(ConfigInformationBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# <- driver_list ->
class DriverListBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class TypeUnitsBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    namekey: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class DataTypeBase(BaseModel):

    id: Optional[int] = Field(..., alias="id")
    namekey: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class TypeByteOrderBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    namekey: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class TypePointListBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    namekey: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class TypePointBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    type: Optional[int] = Field(..., alias="type")
    namekey: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class TypeClassBase(BaseModel):
    id: Optional[int] = Field(..., alias="id")
    name: Optional[str] = Field(..., alias="namekey")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class TypeControlGroupBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    namekey: Optional[str] = None
    description: Optional[str] = None
    attributes: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True

class PointBase(BaseModel):
    id: Optional[int] = None
    id_pointkey: Optional[str] = None
    index: Optional[int] = None
    parent: Optional[int] = None
    # --------------------------------------------------
    id_template: Optional[int] = None
    #
    id_pointclass_type: Optional[int] = None
    id_config_information: Optional[int] = None
    id_point_list_type: Optional[int] = None
    name: Optional[str] = None
    nameedit: Optional[bool] = None
    id_type_units: Optional[int] = None
    unitsedit: Optional[bool] = None
    id_pointtype: Optional[int] = None
    register: Optional[int] = None
    id_type_datatype: Optional[int] = None
    id_type_byteorder: Optional[int] = None
    slope: Optional[float] = None
    slopeenabled: Optional[bool] = None
    offset: Optional[float] = None
    offsetenabled: Optional[bool] = None
    multreg: Optional[int] = None
    multregenabled: Optional[bool] = None
    userscaleenabled: Optional[bool] = None
    invalidvalue: Optional[int] = None
    invalidvalueenabled: Optional[bool] = None
    id_control_group: Optional[int] = None
    extendednumpoints: Optional[int] = None
    active: Optional[bool] = False
    extendedregblocks: Optional[int] = None
    status: Optional[bool] = None
    function: Optional[str] = None
    constants: Optional[str] = None

    class Config:
        orm_mode = True

class ManualPointBase(BaseModel):
    id: Optional[int] = None
    index: Optional[int] = None
    parent: Optional[int] = None
    id_device_type: Optional[int] = None
    id_pointclass_type: Optional[int] = None
    id_config_information: Optional[int] = None
    id_pointkey: Optional[str] = None
    id_point_list_type: Optional[int] = None
    name: Optional[str] = None
    nameedit: Optional[bool] = None
    id_type_units: Optional[int] = None
    unitsedit: Optional[bool] = None
    id_pointtype: Optional[int] = None
    register: Optional[int] = None
    id_type_datatype: Optional[int] = None
    id_type_byteorder: Optional[int] = None
    slope: Optional[float] = None
    slopeenabled: Optional[int] = None
    offset: Optional[float] = None
    offsetenabled: Optional[bool] = None
    multreg: Optional[int] = None
    multregenabled: Optional[bool] = None
    userscaleenabled: Optional[bool] = None
    invalidvalue: Optional[int] = None
    invalidvalueenabled: Optional[bool] = None
    id_control_group: Optional[int] = None
    extendednumpoints: Optional[int] = None
    extendedregblocks: Optional[int] = None
    function: Optional[str] = None
    constants: Optional[str] = None
    active: Optional[bool] = False
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class PointOutBase(PointBase):
    #
    type_units: Optional[TypeUnitsBase] = None
    type_datatype: Optional[DataTypeBase] = None
    type_byteorder: Optional[TypeByteOrderBase] = None
    type_point_list: Optional[TypePointListBase] = None
    type_point: Optional[TypePointBase] = None
    type_class: Optional[TypeClassBase] = None
    type_control: Optional[TypeControlGroupBase] = None

    class Config:
        orm_mode = True

class ControlGroupPointBase(TypeControlGroupBase):
    children: Optional[List[PointOutBase]] = None
class PointUpdateBase(PointBase):
    # id : Optional[int] = None
    equation: Optional[int] = Field(..., examples=[1], nullable=True)

    # id_pointkey : Optional[int] = None
    # id_template : Optional[int] = None
    class Config:
        orm_mode = True
        # fields = {'id_pointkey': {'exclude': True}}


class PointChangeNumberBase(BaseModel):
    id_template: Optional[int] = None
    number_point: Optional[int] = Field(None, ge=1)


class PointDataType(BaseModel):
    id: int = Field(..., alias="id")
    namekey: str = Field(..., alias="data_type")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class PointByteOrder(BaseModel):
    id: int = Field(..., alias="id")
    namekey: str = Field(..., alias="byte_order")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class PointUnit(BaseModel):
    id: int = Field(..., alias="id")
    namekey: str = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class PointOutBase(PointBase):
    #
    type_units: Optional[TypeUnitsBase] = None
    type_datatype: Optional[DataTypeBase] = None
    type_byteorder: Optional[TypeByteOrderBase] = None
    type_point_list: Optional[TypePointListBase] = None
    type_point: Optional[TypePointBase] = None
    type_class: Optional[TypeClassBase] = None
    type_control: Optional[TypeControlGroupBase] = None

    class Config:
        orm_mode = True


# <- register_list ->
class TypeFunctionBase(BaseModel):
    id: Optional[int] = Field(..., nullable=True, alias="id")
    namekey: Optional[str] = Field(..., nullable=True, alias="Function")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class RegisterBase(BaseModel):
    id: Optional[int] = None
    id_template: Optional[int] = None
    addr: Optional[int] = 0
    count: Optional[int] = 0
    id_type_function: Optional[int] = None
    status: Optional[bool] = True

    class Config:
        orm_mode = True


class RegisterListInputBase(BaseModel):
    id_template: Optional[int] = None
    registers: Optional[list[RegisterBase]] = None


class RegisterConfigOutBase(BaseModel):

    register_list: Optional[list[RegisterBase]] = None
    type_function: Optional[list[TypeFunctionBase]] = None

    class Config:
        orm_mode = True


class RegisterListBase(RegisterBase):
    id: Optional[int] = None
    # --------------------------------------------------
    type_function: Optional[TypeFunctionBase] = None

    class Config:
        orm_mode = True


# <- device_type ->
class DeviceTypeBase(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


# <- Communication ->
# class CommunicationBase(BaseModel):
#     name: Optional[str] = None
#     namekey: Optional[str] = None
#     id_driver_list: Optional[int] = None
#     id_type_baud_rates: Optional[int] = None
#     id_type_parity: Optional[int] = None
#     id_type_stopbits: Optional[int] = None
#     id_type_timeout: Optional[int] = None
#     id_type_debug_level: Optional[int] = None
#     # driver_list: DeviceListOut
#     # note1: str
#     # note1: str
#     # status: bool = True

# class CommunicationOut(CommunicationBase):
#     id: int
#     driver_list: DeviceListOut
#     # driver_list: List[DeviceListOut]
#     class Config():
#         orm_mode = True
# class CommunicationCreate(CommunicationBase):
#     id: int
#     driver_list: DriverListBase
#     class Config:
#         orm_mode = True


class type_logging_interval(BaseModel):
    id: int = Field(..., alias="id")
    namekey: str = Field(..., alias="time")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True


class loggingIntervalOut(BaseModel):
    # id: int = Field(..., alias='id')
    # namekey: str = Field(..., alias='Logging_Interval')
    interval: list[type_logging_interval] = None

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
        from_attributes = True
