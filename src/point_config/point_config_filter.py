from typing import Optional

from pydantic.main import BaseModel


class PointTypeNames(BaseModel):
    POINT = "POINT"
    MPPT_POINT = "MPPT_POINT"
    MPPT_VOLTAGE = "MPPT_VOLTAGE"
    MPPT_CURRENT = "MPPT_CURRENT"
    MPPT_STRING = "MPPT_STRING"
    MPPT_PANEL = "MPPT_PANEL"
    CONTROL_GROUP = "CONTROL_GROUP"


class PointType(BaseModel):
    POINT = 266
    MPPT_POINT = 277
    MPPT_VOLTAGE = 274
    MPPT_CURRENT = 275
    MPPT_STRING = 276
    MPPT_PANEL = 278
    CONTROL_GROUP = 0
