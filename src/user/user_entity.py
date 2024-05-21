# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import Integer, String, DATETIME, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime

from ..config import config


class User(config.Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    salt: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    create_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
    updated_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
    create_by: Mapped[str] = mapped_column(String, nullable=True)
    updated_by: Mapped[str] = mapped_column(String, nullable=True)
    last_login: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)

