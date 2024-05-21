# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from ..config import config


class Role(config.Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=False)


class UserRoleMap(config.Base):
    __tablename__ = "user_role_map"

    id_role: Mapped[int] = mapped_column(Integer, ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
                                    primary_key=True, nullable=False)
    id_user: Mapped[int] = mapped_column(Integer, ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
                                         primary_key=True, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    user = relationship("User", foreign_keys=[id_user])
    role = relationship("Role", foreign_keys=[id_role])


class RoleScreenMap(config.Base):
    __tablename__ = "role_screen_map"

    id_role: Mapped[int] = mapped_column(Integer, ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"),
                                         primary_key=True, nullable=False)
    id_screen: Mapped[int] = mapped_column(Integer, ForeignKey("screen.id", ondelete="CASCADE", onupdate="CASCADE"),
                                           primary_key=True, nullable=False)
    auths: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)

    role = relationship("Role", foreign_keys=[id_role])
    screen = relationship("Screen", foreign_keys=[id_screen])

