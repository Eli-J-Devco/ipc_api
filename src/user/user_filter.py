from typing import Optional

from pydantic.main import BaseModel


class GetUserFilter(BaseModel):
    status: Optional[bool] = None
