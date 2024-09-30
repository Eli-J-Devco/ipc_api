# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional, Any
from pydantic.fields import Field
from pydantic import BaseModel
import enum

class Action(enum.Enum):
    
    ControlModify = "Control/Modify"
    ResponseAPI="Init/API/Response"
    
class Device(BaseModel):
    id_device: Optional[int] = None
    mode: Optional[int] = None

class Devices(list[Device]):
    pass

