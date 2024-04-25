from typing import Optional

from pydantic import BaseModel

from ..point.point_model import PointBase
from ..point_control.point_control_model import PointControl
from ..point_mppt.point_mppt_model import PointMppt
from ..register_block.register_block_model import RegisterBlock


class Template(BaseModel):
    name: Optional[str] = None
    id_device_group: Optional[int] = None
    status: Optional[bool] = True
    type: Optional[int] = 1


class TemplateOutput(BaseModel):
    points: list[PointBase] = None
    point_mppt: list[PointMppt] = None
    register_block: list[RegisterBlock] = None
    control_group: list[PointControl] = None
