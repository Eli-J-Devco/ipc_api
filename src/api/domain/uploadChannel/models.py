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


class Upload_channel(Base):
    __tablename__ = "upload_channel"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_type_protocol = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    uploadurl = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    selected_upload = Column(String(255), nullable=True)
    id_type_logging_interval = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    allow_remote_configuration = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
    type_protocol  = relationship('Config_information', foreign_keys=[id_type_protocol])
    type_logging_interval= relationship('Config_information', foreign_keys=[id_type_logging_interval])
    
class Upload_channel_device_map(Base):
    __tablename__ = "upload_channel_device_map"
    id_upload_channel = Column(Integer, ForeignKey(
        "upload_channel.id", ondelete="CASCADE", onupdate="CASCADE"),  primary_key=True,nullable=True)
    id_device = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"),nullable=True)
    upload_channel= relationship('Upload_channel', foreign_keys=[id_upload_channel])
    device_list= relationship('Device_list', foreign_keys=[id_device])
    