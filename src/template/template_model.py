from typing import Optional

from pydantic import BaseModel

from ..point.point_model import PointOutput
from ..point_config.point_config_model import PointListControlGroupChildren
from ..point_control.point_control_model import PointControl
from ..point_mppt.point_mppt_model import PointMppt
from ..project_setup.project_setup_model import ConfigInformationShort
from ..register_block.register_block_model import RegisterBlock


class Template(BaseModel):
    name: Optional[str] = None
    id_device_group: Optional[int] = None
    status: Optional[bool] = True
    type: Optional[int] = 1


class TemplateOutput(BaseModel):
    points: list[PointOutput] = None
    point_mppt: list[PointMppt] = None
    register_blocks: list[RegisterBlock] = None
    point_controls: list[PointListControlGroupChildren] = None


class TemplateConfig(BaseModel):
    data_type: list[ConfigInformationShort] = None
    byte_order: list[ConfigInformationShort] = None
    point_unit: list[ConfigInformationShort] = None
    type_point: list[ConfigInformationShort] = None
    type_point_list: list[ConfigInformationShort] = None
    type_class: list[ConfigInformationShort] = None
    type_function: list[ConfigInformationShort] = None
