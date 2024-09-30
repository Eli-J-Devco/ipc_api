# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime

from sqlalchemy import DOUBLE, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from configs.config import orm_provider as config


class PointListType(config.Base):
    __tablename__ = "point_list_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    namekey: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=True)





