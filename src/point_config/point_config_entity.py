# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import config


class PointListType(config.Base):
    __tablename__ = "point_list_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    namekey: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=True)


class PointclassType(config.Base):
    __tablename__ = "pointclass_type"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=True)


class PointListControlGroup(config.Base):
    __tablename__ = "point_list_control_group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_template: Mapped[int] = mapped_column(Integer, ForeignKey("template_library.id",
                                                                 ondelete="CASCADE",
                                                                 onupdate="CASCADE"),
                                             nullable=False)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    namekey: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    attributes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[int] = mapped_column(Integer, nullable=True)

    template_library = relationship("Template", foreign_keys=[id_template])