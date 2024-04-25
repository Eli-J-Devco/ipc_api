from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..point.point_entity import Point
from ..config import config


class PointControl(Point):
    pass

