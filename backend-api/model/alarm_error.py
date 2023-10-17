from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base


class error_comparison(Base):
    __tablename__ = "error_comparison"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class error_level(Base):
    __tablename__ = "error_level"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class error_type(Base):
    __tablename__ = "error_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class alarm(Base):
    __tablename__ = "alarm"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device = Column(Integer, ForeignKey(
        "device.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_error = Column(Integer, ForeignKey(
        "error.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    opened = Column(String(255), nullable=False)
    closed = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)


class error(Base):
    __tablename__ = "error"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_device_group = Column(Integer, ForeignKey(
        "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_error_level = Column(Integer, ForeignKey(
        "error_level.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_error_type = Column(Integer, ForeignKey(
        "error_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    error_code = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
    comparison = Column(String(255), nullable=True)
    point = Column(String(255), nullable=False)
    id_error_comparison = Column(Integer, ForeignKey(
        "error_comparison.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    value = Column(DOUBLE, nullable=False, default=True)
    enable = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
