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
    ControlDevice as ControlDeviceModel


class WriteParameter(ControlDeviceModel):
    pass

class WritePointStatus(BaseModel):
    code: Optional[int] = None
    data: Optional[Any] = None
    exception_code: Optional[str] = None
    address: Optional[int] = None
    msg: Optional[str] = None
    status: Optional[int] = None
class WriteStatus(WritePointStatus):
    pass
class FeedbackWeb(BaseModel):
    time_stamp: Optional[str] = None
    status: Optional[int] = None
    token: Optional[str] = None
    id_device: Optional[int] = None 

class Action(enum.Enum):
    PathTopicFeedBackWeb = "Control/Feedbacksetup"
    PathTopicFeedBackAutoControl = "Control/FeedbackAuto"
    WriteStatusSuccess=200
    WriteStatusError=400
    