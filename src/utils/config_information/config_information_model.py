# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional, Any
from pydantic.fields import Field
from pydantic import BaseModel
import enum

class PointConfigInforAction(enum.Enum):
    MPPT = "MPPT"
    MPPTVolt ="MPPTVolt"
    MPPTAmps ="MPPTAmps"
    StringAmps = "StringAmps"
    Field = "Field"
    Panel= "Panel"
    Internal= "Internal"