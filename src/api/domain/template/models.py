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


class Template_library(Base):
    __tablename__ = "template_library"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_device_group = Column(Integer, ForeignKey(
        "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # id_template_type = Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    
    # device_group = relationship("Device_group", back_populates='templates_library')
    point_list= relationship("Point_list", back_populates='template_library')
    register_list= relationship("Register_block", back_populates='template_library')
# 