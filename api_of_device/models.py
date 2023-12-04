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


class Language_list(Base):
    __tablename__ = "language_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
# 
class device_type(Base):
    __tablename__ = "device_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)

# 
class device_group(Base):
    __tablename__ = "device_group"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    template= relationship('template_library', foreign_keys=[id_template])
# 
class template_library(Base):
    __tablename__ = "template_library"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    
# 
class Project_setup(Base):
    __tablename__ = "project_setup"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    administrative_contact = Column(String(255), nullable=True)

    id_first_page_on_login = Column(Integer, ForeignKey(
        "page.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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
    first_page_on_login= relationship('Page', foreign_keys=[id_first_page_on_login])
    enable_search_modbus_rtu_device= Column(Boolean, nullable=False, default=False)
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
    device_virtual= Column(Boolean, nullable=True, default=True)
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
    type_ethernet  = relationship('Config_information', foreign_keys=[id_type_ethernet])
# 
class Upload_channel(Base):
    __tablename__ = "upload_channel"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_type_protocol = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    uploadurl = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    selected_upload = Column(String(255), nullable=True)
    id_type_logging_interval = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    allow_remote_configuration = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)
    type_protocol  = relationship('Config_information', foreign_keys=[id_type_protocol])
    type_logging_interval= relationship('Config_information', foreign_keys=[id_type_logging_interval])
# 
class Page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
class Test(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)