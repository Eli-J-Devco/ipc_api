# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base
from sqlalchemy import (DOUBLE, Boolean, Column, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


# 
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
# 
class Device_list(Base):
    __tablename__ = "device_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_device_type = Column(Integer, ForeignKey(
        "device_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_communication = Column(Integer, ForeignKey(
        "communication.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_device_group = Column(Integer, ForeignKey(
        "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    rtu_bus_address = Column(Integer, nullable=True)
    tcp_gateway_ip = Column(String(255), nullable=True)
    tcp_gateway_port = Column(Integer, nullable=True)
    enable = Column(Boolean, nullable=True, default=True)
    point = Column(Integer, nullable=True)
    pv = Column(Integer, nullable=True)
    model = Column(Integer, nullable=True)
    function = Column(Integer, nullable=True)
    point_p = Column(String(255), nullable=True)
    value_p = Column(DOUBLE, nullable=True)
    send_p = Column(Boolean, nullable=True, default=True)
    point_q = Column(String(255), nullable=True)
    value_q = Column(DOUBLE, nullable=True)
    send_q = Column(Boolean, nullable=True, default=True)
    point_pf = Column(String(255), nullable=True)
    value_pf = Column(DOUBLE, nullable=True)
    send_pf = Column(Boolean, nullable=True, default=True)
    max = Column(DOUBLE, nullable=True)
    allow_error = Column(DOUBLE, nullable=True)
    enable_poweroff = Column(Boolean, nullable=True, default=True)
    inverter_shutdown = Column(TIMESTAMP(timezone=True),
                               nullable=True)
    status = Column(Boolean, nullable=True, default=True)
# 
class Config_information(Base):
    __tablename__ = "config_information"
    id = Column(Integer, primary_key=True, nullable=False)
    parent = Column(Integer, nullable=True)
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    value = Column(Integer, nullable=True)
    type = Column(Integer, nullable=True)
    id_type = Column(Integer, ForeignKey(
        "config_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
# 
class Driver_list(Base):
    __tablename__ = "driver_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

# 
class Communication(Base):
    __tablename__ = "communication"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=False)
    id_driver_list = Column(Integer, ForeignKey(
        "driver_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_type_baud_rates = Column(Integer, nullable=True)
    id_type_parity = Column(Integer, ForeignKey(
        "type_parity.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_type_stopbits = Column(Integer, ForeignKey(
        "type_stopbits.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_type_timeout = Column(Integer, ForeignKey(
        "type_timeout.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_type_debug_level = Column(Integer, ForeignKey(
        "type_debug_level.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    note1 = Column(String(255), nullable=True)
    note2 = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    driver_list  = relationship('Driver_list', foreign_keys=[id_driver_list])
# 

class Ethernet(Base):
    __tablename__ = "ethernet"
    id = Column(Integer, primary_key=True, nullable=False)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    namekey = Column(String(255), nullable=False)
    id_type_ethernet = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    allow_dns = Column(Boolean, nullable=True, default=False)
    ip_address = Column(String(255), nullable=True)
    subnet_mask = Column(String(255), nullable=True)
    gateway= Column(String(255), nullable=True)
    mtu = Column(String(255), nullable=True)
    dns1 = Column(String(255), nullable=True)
    dns2 = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    type_ethernet  = relationship('Config_information')