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

# <- site_information ->
class SiteInformBase(BaseModel):
    # id_project_setup: int
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    administrative_contact: Optional[str] = None

class SiteInformOut(SiteInformBase):
    id: Optional[int] = None
   
    class Config:
        orm_mode = True
class SiteInformCreate(SiteInformBase):
    class Config:
        orm_mode = True
class SiteInformUpdate(SiteInformBase):
    class Config:
        orm_mode = True 