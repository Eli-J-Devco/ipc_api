from typing import Optional

from ..devices_model import Point


class UpdatePoint(Point):
    id_template: Optional[int] = None
    status: Optional[int] = None

    class Config:
        orm_mode = True
