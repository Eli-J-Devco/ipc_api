# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field

from ..project_setup.project_setup_model import ConfigInformationShort


class PointShort(BaseModel):
    id_pointkey: Optional[str] = None
    alias: Optional[str] = None


class PointBase(PointShort):
    id: Optional[int] = None
    parent: Optional[int] = None
    id_pointclass_type: Optional[int] = 1
    id_point_list_type: Optional[int] = None
    name: Optional[str] = None
    nameedit: Optional[bool] = None
    id_type_units: Optional[int] = None
    unitsedit: Optional[bool] = None
    id_pointtype: Optional[int] = None
    id_config_information: Optional[int] = 266
    register_value: Optional[int] = Field(None, alias="register")
    id_type_datatype: Optional[int] = None
    id_type_byteorder: Optional[int] = None
    id_type_function: Optional[int] = None
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
    extendedregblocks: Optional[int] = None
    function: Optional[str] = None
    constants: Optional[str] = None
    active: Optional[bool] = None
    status: Optional[bool] = True
    control_type_input: Optional[int] = None


class PointOutput(PointBase):
    type_units: Optional[ConfigInformationShort] = None
    type_datatype: Optional[ConfigInformationShort] = None
    type_byteorder: Optional[ConfigInformationShort] = None
    type_point_list: Optional[ConfigInformationShort] = None
    type_point: Optional[ConfigInformationShort] = None
    type_class: Optional[ConfigInformationShort] = None
    type_function: Optional[ConfigInformationShort] = None
    type_control_input: Optional[ConfigInformationShort] = None

    class Config:
        orm_mode = True
        from_attribute = True


class ManualPoint(PointBase):
    id_device_type: Optional[int] = None

    class Config:
        orm_mode = True
