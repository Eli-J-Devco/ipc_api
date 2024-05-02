from typing import Optional

from pydantic.main import BaseModel


class GetTemplateFilter(BaseModel):
    id: Optional[int] = None
    type: Optional[int] = None
