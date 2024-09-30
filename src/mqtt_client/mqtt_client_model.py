# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional,Any
from pydantic import BaseModel

class MQTTConfigBase(BaseModel):
    host : Optional[str] = "127.0.0.1"
    port: Optional[int] = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    serial_number : Optional[str] =""

class MQTTMsg(BaseModel):
    topic : Optional[str] = None
    payload: Optional[Any] = None
    
class MQTTMsgs(BaseModel):
    msgs: list[MQTTMsg]=[]