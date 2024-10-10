# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Any, Optional

from pydantic import BaseModel
from pydantic.fields import Field
import enum
from src.device_manager.control_device.control_device_model import \
    ControlDevice as ControlDeviceModel , ControlModeDevice as ControlModeDeviceModel

class ParameterWeb(ControlDeviceModel):
    device_token: Optional[str] = None
class ParameterAuto(ControlDeviceModel):
    device_token: Optional[str] = None
class ParameterMode(ControlModeDeviceModel):
    device_token: Optional[str] = None
    