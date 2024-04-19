from typing import Optional

from pydantic.main import BaseModel


class PointType:
    POINT = 266
    MPPT_POINT = 277
    MPPT_VOLTAGE = 274
    MPPT_CURRENT = 275
    MPPT_STRING = 276
    MPPT_PANEL = 278
    CONTROL_GROUP = 0


class GetPointFilter(BaseModel):
    id_template: int
    point_type: Optional[int] = None
