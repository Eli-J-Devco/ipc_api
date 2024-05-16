from typing import Optional

from pydantic import BaseModel

from ..point.point_model import PointOutput
from ..point_config.point_config_model import PointListControlGroupChildren


class PointControl(BaseModel):
    id: Optional[int]
    id_template: Optional[int]
    name: Optional[str]
    namekey: Optional[str]
    description: Optional[str] = None
    value: Optional[int] = None
    attributes: Optional[int] = 0
    status: Optional[int] = 1


class PointControlRefresh(BaseModel):
    points: list[PointOutput] = None
    point_controls: list[PointListControlGroupChildren] = None
