# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional,Any
from pydantic.fields import Field
from pydantic import BaseModel
import enum

# class DeviceSub(BaseModel):


class Action(enum.Enum):
    
    PathTopicCreateUpdateDev = "Init/API/Requests"
    PathTopicWeb = "Control/Write"
    PathTopicAutoControl = "Control/Auto"
    PathTopicModeSys = "Control/Setup/Mode/Feedback"
    PathTopicMeter = "Meter/Monitor"
    
    CreateTCPDev="CreateTCPDev"
    CreateRS485Dev="CreateRS485Dev"
    DeleteDev="DeleteDev"
    UpdateDev="UpdateDev"
    UpdateTemplate="UpdateTemplate"
    DeleteTemplate="DeleteTemplate"
    UpdatePortRS485="UpdatePortRS485"
    UpdateUploadChannels="UpdateUploadChannels"
    CreateNoLogDev="CreateNoLogDev"

class DeviceSub(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None 
    connect_type: Optional[str] = None 
    id_communication: Optional[int] = None
    mode: Optional[int] = None
    device_type_value: Optional[int] = None
    
class UploadChannel(BaseModel):
    id: Optional[int] = None
    
class PayloadSub(BaseModel):
    id_communication: Optional[int] = None
    device: list[DeviceSub] = None
    
    # DeleteDev
    delete_mode: Optional[int] = None
    # UpdateDev
    id:Optional[int] = None
    code:Optional[int] = None
    # UpdateTemplate
    # UpdatePortRS485
    # UpdateUploadChannels
    upload_channels:list[UploadChannel] = None
    # CreateNoLogDev
    
class MqttMsgSub(BaseModel):
    CODE: Optional[str] = None 
    PAYLOAD : Optional[PayloadSub] = None 

class StatusJob(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    status: Optional[int] = None #1=success 0= error
    message: Optional[str] = None
    mode: Optional[int] = None 
class StatusJobs(BaseModel):
    jobs :list[StatusJob]=[]
    code: Optional[str] = None
    timestamp: Optional[str] = None
    
class MqttDataSub(BaseModel):
    topic : Optional[str] = None
    message: Optional[Any] = None