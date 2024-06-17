# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from typing import Optional

from pydantic.main import BaseModel


class Pagination(BaseModel):
    page: Optional[int]
    limit: Optional[int]


class PaginationResponse(Pagination):
    prev: Optional[str]
    next: Optional[str]
    total: int
    data: list
