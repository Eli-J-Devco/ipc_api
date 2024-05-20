from typing import Optional

from pydantic import BaseModel


class Point(BaseModel):
    id: Optional[int] = None
    parent: Optional[int] = None
    id_pointkey: Optional[str] = None
    id_template: Optional[int] = None
    name: Optional[str] = None
    id_config_information: Optional[int] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True
