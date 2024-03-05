# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
from datetime import datetime

from sqlalchemy import (DOUBLE, BigInteger, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, Text, create_engine)
from sqlalchemy.orm import (declarative_base, mapped_column, relationship,
                            sessionmaker)
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from database.db import Base, engine


class Error_comparison(Base):
    __tablename__ = "error_comparison"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
class Alarm(Base):
    __tablename__ = "alarm"
    id = Column(BigInteger, primary_key=True, nullable=False)
    id_device = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_error = Column(Integer, ForeignKey(
        "error.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    opened =  Column(Boolean, nullable=False, default=False)
    closed = Column(Boolean, nullable=False, default=False)
    status = Column(Boolean, nullable=False, default=True)
class Error(Base):
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
    time_limit_alarm  = Column(Integer, nullable=False, default=5)
    number_limit_alarm  = Column(Integer, nullable=False, default=5)