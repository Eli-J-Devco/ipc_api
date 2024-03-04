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


# class Page(Base):
#     __tablename__ = "page"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)
# class Config_information(Base):
#     __tablename__ = "config_information"
#     id = Column(Integer, primary_key=True, nullable=False)
#     parent = Column(Integer, nullable=True)
#     name = Column(String(255), nullable=True)
#     namekey = Column(String(255), nullable=True)
#     description = Column(Text, nullable=True)
#     value = Column(Integer, nullable=True)
#     type = Column(Integer, nullable=True)
#     id_type = Column(Integer, ForeignKey(
#         "config_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     status = Column(Boolean, nullable=False, default=True)
class Project_setup(Base):
    __tablename__ = "project_setup"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    administrative_contact = Column(String(255), nullable=True)

    id_first_page_on_login = Column(Integer, ForeignKey(
        "screen.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_logging_interval = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    id_scheduled_upload_time = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    number_times_retry = Column(Integer, nullable=False, default=3)
    id_time_wait_before_retry = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_upload_debug_information = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    enable_upload_data_on_alarm_status = Column(
        Boolean, nullable=False, default=True)
    enable_upload_data_on_low_disk = Column(
        Boolean, nullable=False, default=True)
    enable_upload_data_on_system_startup = Column(
        Boolean, nullable=False, default=True)
    link_remote_access = Column(String(255), nullable=True)
    allow_remote_access = Column(Boolean, nullable=False, default=False)
    enable_static_routing = Column(Boolean, nullable=False, default=False)

    id_time_zone = Column(Integer, ForeignKey(
        "time_zone.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Time1cycle = Column(DOUBLE(), nullable=False, default=5)
    sampling_time1cycle = Column(DOUBLE(), nullable=False, default=15)

    enable_zero_export = Column(Boolean, nullable=False, default=False)
    value_zero_export = Column(DOUBLE(), nullable=False, default=100)

    enable_limit_energy = Column(Boolean, nullable=False, default=False)
    value_limit_energy = Column(DOUBLE(), nullable=False, default=100)

    modhopper1 = Column(Integer, nullable=True)
    modhopper2 = Column(Integer, nullable=True)
    modhopper_key = Column(String(255), nullable=True)
    modhopper_rf_config = Column(Integer, nullable=True)
    modhopper_rf_channel = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    enable_search_modbus_rtu_device= Column(Boolean, nullable=False, default=True)
    logging_interval  = relationship('Config_information', foreign_keys=[id_logging_interval])
    first_page_on_login= relationship('Screen', foreign_keys=[id_first_page_on_login])
    enable_search_modbus_rtu_device= Column(Boolean, nullable=False, default=False)
    # number_limit_alarm= Column(Integer, nullable=True)
    # time_limit_alarm= Column(Integer, nullable=True)
    # mode_control = Column(Integer, nullable=False,default=0)