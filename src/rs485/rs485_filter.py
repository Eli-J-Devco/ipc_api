from typing import Optional

from pydantic import BaseModel


class RS485Filter(BaseModel):
    id: Optional[int]

