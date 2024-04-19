from typing import Optional

from pydantic import BaseModel
from pydantic.fields import Field


class PointBase(BaseModel):
    id: Optional[int] = None
    index: Optional[int] = None
    parent: Optional[int] = None
    id_device_type: Optional[int] = None
    id_pointclass_type: Optional[int] = None
    id_pointkey: Optional[str] = None
    id_point_list_type: Optional[int] = None
    name: Optional[str] = None
    nameedit: Optional[bool] = None
    id_type_units: Optional[int] = None
    unitsedit: Optional[bool] = None
    id_pointtype: Optional[int] = None
    id_config_information: Optional[int] = None
    register_value: Optional[int] = Field(None, alias="register")
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
    extendedregblocks: Optional[int] = None
    function: Optional[str] = None
    constants: Optional[str] = None
    active: Optional[bool] = None
    status: Optional[bool] = None

    class Config:
        orm_mode = True


class MPPTPanel(PointBase):
    pass


class MPPTString(PointBase):
    children: Optional[list[MPPTPanel]] = None


class MPPTPoint(PointBase):
    children: Optional[list[MPPTString | PointBase]] = None
