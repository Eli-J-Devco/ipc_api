# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic.main import BaseModel


class GetTemplateFilter(BaseModel):
    id: Optional[int] = None
    type: Optional[int] = None
