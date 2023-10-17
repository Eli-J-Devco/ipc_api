from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base


class language_list(Base):
    __tablename__ = "language_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, nullable=False)
    fullname = Column(String(255), nullable=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    last_login = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    date_joined = Column(TIMESTAMP(timezone=True),
                         nullable=True)
    id_language = Column(Integer, ForeignKey(
        "language_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    status = Column(Boolean, nullable=False, default=True)


class auth_role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class auth_user_role_map(Base):
    __tablename__ = "user_role_map"
    id_user = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    status = Column(Boolean, nullable=False, default=True)


class auth_role_screen_map(Base):
    __tablename__ = "role_screen_map"
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_screen = Column(Integer, ForeignKey(
        "screen.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    auths = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class screen(Base):
    __tablename__ = "screen"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
