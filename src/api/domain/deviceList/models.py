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


class Device_list(Base):
    __tablename__ = "device_list"
    id = Column(Integer, primary_key=True, nullable=False)
    table_name= Column(String(255), nullable=False)
    view_table=Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    device_virtual= Column(Boolean, nullable=True, default=True)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_device_type = Column(Integer, ForeignKey(
        "device_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_communication = Column(Integer, ForeignKey(
        "communication.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    # 12/03/2024
    # id_device_group = Column(Integer, ForeignKey(
    #     "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    rtu_bus_address = Column(Integer, nullable=True)
    tcp_gateway_ip = Column(String(255), nullable=True)
    tcp_gateway_port = Column(Integer, nullable=True)
    enable = Column(Boolean, nullable=True, default=True)
    
    max_watt= Column(DOUBLE, nullable=True)
    min_watt_in_percent= Column(DOUBLE, nullable=True)
    compensate_watt_factor= Column(DOUBLE, nullable=True)
    battery_mode= Column(Boolean, nullable=True, default=True)
    battery_normal_watt= Column(DOUBLE, nullable=True)
    battery_reduce_watt= Column(DOUBLE, nullable=True)
    battery_threshold_off_limit_in_v= Column(DOUBLE, nullable=True)
    battery_threshold_reduce_limit_in_v= Column(DOUBLE, nullable=True)
    battery_threshold_normal_limit_in_v= Column(DOUBLE, nullable=True)
    battery_threshold_on_limit_in_v= Column(DOUBLE, nullable=True)
    battery_priority= Column(Integer, nullable=True)
    
    point = Column(Integer, nullable=True)
    pv = Column(Integer, nullable=True)
    model = Column(Integer, nullable=True)
    function = Column(Integer, nullable=True)
    point_p = Column(Integer, ForeignKey(
        "point_list.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True) #id
    value_p = Column(DOUBLE, nullable=True)
    send_p = Column(Boolean, nullable=True, default=True)
    point_q= Column(Integer, ForeignKey(
        "point_list.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True) #id
    value_q = Column(DOUBLE, nullable=True)
    send_q = Column(Boolean, nullable=True, default=True)
    point_pf = Column(Integer, ForeignKey(
        "point_list.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True) #id
    value_pf = Column(DOUBLE, nullable=True)
    send_pf = Column(Boolean, nullable=True, default=True)
    max = Column(DOUBLE, nullable=True)
    allow_error = Column(DOUBLE, nullable=True)
    enable_poweroff = Column(Boolean, nullable=True, default=True)
    inverter_shutdown = Column(TIMESTAMP(timezone=True),
                               nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    
    # 
    communication  = relationship('Communication', foreign_keys=[id_communication]) 
    # point_p_list = relationship('Point_list', foreign_keys=[point_p])
    # point_q_list  = relationship('Point_list', foreign_keys=[point_q])
    # point_pf_list  = relationship('Point_list', foreign_keys=[point_pf])
    # 
    # # device_group  = relationship('Device_group', foreign_keys=[id_device_group])
    # 12/03/2024
    # device_group= relationship("Device_group", back_populates="device_list")
    device_type = relationship('Device_type', foreign_keys=[id_device_type])
    
class Device_mppt(Base):
    __tablename__ = "device_mppt"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_list = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=True)
    voltage= Column(DOUBLE, nullable=True)
    current= Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_list  = relationship('Device_list', foreign_keys=[id_device_list]) 
class Device_mppt_string(Base):
    __tablename__ = "device_mppt_string"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_mppt = Column(Integer, ForeignKey(
        "device_mppt.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=True)
    panel= Column(Integer, nullable=True)
    current= Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_mptt  = relationship('Device_mppt', foreign_keys=[id_device_mppt]) 
class Device_panel(Base):
    __tablename__ = "device_panel"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_string = Column(Integer, ForeignKey(
        "device_mppt_string.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    name = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)
    pmax = Column(DOUBLE, nullable=True)
    vmpp = Column(DOUBLE, nullable=True)
    impp = Column(DOUBLE, nullable=True)
    voc= Column(DOUBLE, nullable=True)
    isc= Column(DOUBLE, nullable=True)
    weight= Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_mppt_string = relationship('Device_mppt_string', foreign_keys=[id_device_string])
    
class Data_panel(Base):
    __tablename__ = "data_panel"
    time =Column(TIMESTAMP(timezone=True), primary_key=True,
                        nullable=True)
    id_device_panel = Column(Integer, ForeignKey(
        "device_panel.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
   
    device_panel = relationship('Device_panel', foreign_keys=[id_device_panel])