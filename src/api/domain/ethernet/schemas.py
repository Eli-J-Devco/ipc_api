# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import uuid
from datetime import datetime
from hashlib import sha256
from typing import List, Optional

# 
from fastapi import APIRouter, Depends, Query
from pydantic import (BaseModel, EmailStr, Field, computed_field,
                      root_validator, validator)
from pydantic.types import conint

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from model.schemas import (ConfigInformationOut, PointByteOrder, PointDataType,
                           PointOutBase, PointUnit, RegisterListBase)


# <- Ethernet ->
class NetworkInfBase(BaseModel):
    namekey: Optional[str] = None
    ip_address: Optional[str] = None
    subnet_mask:  Optional[str] = None
    gateway:  Optional[str] = None
    mtu: Optional[str] = None
    dns1:  Optional[str] = None
    dns2:  Optional[str] = None
    class Config:
        orm_mode = True
class EthernetBase(NetworkInfBase):
    # id_project_setup: int
    name: Optional[str] = None
    # namekey: Optional[str] = None
    id_type_ethernet: Optional[int] = None
    allow_dns: Optional[bool] = None
    # # 
    # ip_address: Optional[str] = None
    # subnet_mask: Optional[str] = None
    # gateway: Optional[str] = None
    # mtu: Optional[str] = None
    # dns1:  Optional[str] = None
    # dns2:  Optional[str] = None
 
    # status: bool = True
class EthernetOut(EthernetBase):
    id: Optional[int] = None
    type_ethernet: ConfigInformationOut #Is it good ?
    class Config:
        orm_mode = True
class EthernetCreate(EthernetBase):
    class Config:
        orm_mode = True

class NetworkInterfaceBase(NetworkInfBase):
    # interface: Optional[str] = None
    # information: Optional[NetworkInfBase] = None
    class Config:
        orm_mode = True
class NetworkBase(BaseModel):
    network:list[NetworkInterfaceBase]
    class Config:
        orm_mode = True