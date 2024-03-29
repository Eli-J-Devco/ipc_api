# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base, engine
from sqlalchemy import (DOUBLE, Boolean, Column, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


# 
class Page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
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

class Language_list(Base):
    __tablename__ = "language_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
# 
class Device_type(Base):
    __tablename__ = "device_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
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

class Template_library(Base):
    __tablename__ = "template_library"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_template_type = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    
    device_group = relationship("Device_group", back_populates='templates_library')
    point_list= relationship("Point_list", back_populates='template_library')
    register_list= relationship("Register_block", back_populates='template_library')
# 
# 
class Point_list(Base):
    __tablename__ = "point_list"
    id = Column(Integer, primary_key=True, nullable=False)
    id_pointkey = Column(Integer, nullable=False)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    nameedit = Column(Boolean, nullable=False, default=True)
    id_type_units = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    unitsedit = Column(Boolean, nullable=False, default=True)
    
    equation = Column(Integer,  ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    config = Column(Integer,  ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    
    register = Column(Integer, nullable=False)
    id_type_datatype = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_byteorder = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    slope = Column(DOUBLE, nullable=False)
    slopeenabled = Column(Boolean, nullable=False, default=True)
    offset = Column(DOUBLE, nullable=False)
    offsetenabled = Column(Boolean, nullable=False, default=True)
    multreg = Column(Integer, nullable=False)
    multregenabled = Column(Boolean, nullable=True, default=True)
    userscaleenabled = Column(Boolean, nullable=False, default=True)
    invalidvalue = Column(Integer, nullable=False)
    invalidvalueenabled = Column(Boolean, nullable=False, default=True)
    extendednumpoints = Column(Integer, nullable=True)
    extendedregblocks = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    function= Column(Text, nullable=True)
    constants=Column(DOUBLE(), nullable=True, default=0)
    # 
    # template_library  = relationship('Template_library', foreign_keys=[id_template])
    type_units  = relationship('Config_information', foreign_keys=[id_type_units])
    type_datatype  = relationship('Config_information', foreign_keys=[id_type_datatype])
    type_byteorder  = relationship('Config_information', foreign_keys=[id_type_byteorder])
    type_point= relationship('Config_information', foreign_keys=[equation])
    type_class= relationship('Config_information', foreign_keys=[config])
    # 
    template_library=relationship("Template_library", back_populates='point_list')
    # 

class Device_group(Base):
    __tablename__ = "device_group"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # template= relationship('Template_library', foreign_keys=[id_template])

    templates_library = relationship("Template_library", back_populates="device_group")
    # 
    device_list= relationship("Device_list", back_populates="device_group")
    
# -----------------------------------------------------
class Screen(Base):
    __tablename__ = "screen"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
# 
class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    role_map=relationship("Role_screen_map", back_populates='role')
# 
class Role_screen_map(Base):
    __tablename__ = "role_screen_map"
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_screen = Column(Integer, ForeignKey(
        "screen.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    auths = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

    ## role  = relationship('Role', foreign_keys=[id_role])
    screen  = relationship('Screen', foreign_keys=[id_screen])
    
    role=relationship("Role", back_populates='role_map')
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
    language  = relationship('Language_list', foreign_keys=[id_language])
# 
class User_role_map(Base):
    __tablename__ = "user_role_map"
    id_user = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    
    status = Column(Boolean, nullable=False, default=True)
    ## user  = relationship('User', foreign_keys=[id_user])
    ## role  = relationship('Role', foreign_keys=[id_role])
    ## role_screen=relationship("Role_screen_map", back_populates='user_role')
    user  = relationship('User')
    role  = relationship('Role')
    
    
    
    # id_user = mapped_column(ForeignKey("user.id"), primary_key=True)
    # id_role = mapped_column(ForeignKey("role.id"), primary_key=True)
    
#  -----------------------------------------------------
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
    point_p_list = relationship('Point_list', foreign_keys=[point_p])
    point_q_list  = relationship('Point_list', foreign_keys=[point_q])
    point_pf_list  = relationship('Point_list', foreign_keys=[point_pf])
    # 
    # device_group  = relationship('Device_group', foreign_keys=[id_device_group])
    device_group= relationship("Device_group", back_populates="device_list")

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
class Device_point_list(Base):
    __tablename__ = "device_point_list"
    id = Column(Integer, primary_key=True, nullable=False)
    id_pointkey = Column(Integer, nullable=False)
    # --------------------------------------------------
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_device_group = Column(Integer, ForeignKey(
        "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_device_list = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_point_list = Column(Integer, ForeignKey(
        "point_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # # ------ delete -------------------------------------------- 
    # name = Column(String(255), nullable=False)
    # nameedit = Column(Boolean, nullable=False, default=True)
    # id_type_units = Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    # unitsedit = Column(Boolean, nullable=False, default=True)
    # equation = Column(Integer, nullable=False, default=True)
    # config = Column(Integer, nullable=False)
    # register = Column(Integer, nullable=False)
    # id_type_datatype = Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # id_type_byteorder = Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # slope = Column(DOUBLE, nullable=False)
    # slopeenabled = Column(Boolean, nullable=False, default=True)
    # offset = Column(DOUBLE, nullable=False)
    # offsetenabled = Column(Boolean, nullable=False, default=True)
    # multreg = Column(Integer, nullable=False)
    # multregenabled = Column(Boolean, nullable=True, default=True)
    # userscaleenabled = Column(Boolean, nullable=False, default=True)
    # invalidvalue = Column(Integer, nullable=False)
    # invalidvalueenabled = Column(Boolean, nullable=False, default=True)
    # extendednumpoints = Column(Integer, nullable=True)
    # extendedregblocks = Column(Integer, nullable=True)
    # status = Column(Boolean, nullable=False, default=True)
    # # 
    # template_library  = relationship('Template_library', foreign_keys=[id_template])
    # device_group  = relationship('Device_group', foreign_keys=[id_device_group])
    # device_list  = relationship('Device_list', foreign_keys=[id_device_list])
    # point_list  = relationship('Point_list', foreign_keys=[id_point_list])
    
    # type_units  = relationship('Config_information', foreign_keys=[id_type_units])
    # type_datatype  = relationship('Config_information', foreign_keys=[id_type_datatype])
    # type_byteorder  = relationship('Config_information', foreign_keys=[id_type_byteorder])
    # 
# 
class Register_block(Base):
    __tablename__ = "register_block"
    id = Column(Integer, primary_key=True, nullable=False)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    addr = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    id_type_function = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    # template_library  = relationship('Template_library', foreign_keys=[id_template])
    type_function  = relationship('Config_information', foreign_keys=[id_type_function])
    template_library=relationship("Template_library", back_populates='register_list')
class Device_register_block(Base):
    __tablename__ = "device_register_block"
    id = Column(Integer, primary_key=True, nullable=False)
    # --------------------------------------------------
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_device_group = Column(Integer, ForeignKey(
        "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_device_list = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_register_block = Column(Integer, ForeignKey(
        "register_block.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # --------------------------------------------------
    # addr = Column(Integer, nullable=False)
    # count = Column(Integer, nullable=False)
    # id_type_function = Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # status = Column(Boolean, nullable=False, default=True)
    template_library  = relationship('Template_library', foreign_keys=[id_template])
    device_group  = relationship('Device_group', foreign_keys=[id_device_group])
    device_list  = relationship('Device_list', foreign_keys=[id_device_list])
    register_block  = relationship('Register_block', foreign_keys=[id_register_block])
    # --------------------------------------------------
    # type_function  = relationship('Config_information', foreign_keys=[id_type_function])   
# 
def create_table(table_name):
    class DynamicTable(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True, autoincrement=True)
        column_1 = Column(String(200))
        column_2 = Column(String(200))

    DynamicTable.__table__.create(engine)
def create_table_device(table_name):
    class DynamicTable(Base):
        __tablename__ = table_name
        time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
        id_device = Column(Integer, ForeignKey(
            "device_list.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True)
        error = Column(Integer, nullable=True)
        low_alarm = Column(Integer, nullable=True)
        high_alarm = Column(Integer, nullable=True)
        serial_number = Column(String(255), nullable=True)
        pt0 = Column(DOUBLE, nullable=True)
        pt1 = Column(DOUBLE, nullable=True)
        pt2 = Column(DOUBLE, nullable=True)
        pt3 = Column(DOUBLE, nullable=True)
        pt4 = Column(DOUBLE, nullable=True)
        pt5 = Column(DOUBLE, nullable=True)
        pt6 = Column(DOUBLE, nullable=True)
        pt7 = Column(DOUBLE, nullable=True)
        pt8 = Column(DOUBLE, nullable=True)
        pt9 = Column(DOUBLE, nullable=True)
        pt10 = Column(DOUBLE, nullable=True)
        pt11 = Column(DOUBLE, nullable=True)
        pt12 = Column(DOUBLE, nullable=True)
        pt13 = Column(DOUBLE, nullable=True)
        pt14 = Column(DOUBLE, nullable=True)
        pt15 = Column(DOUBLE, nullable=True)
        pt16 = Column(DOUBLE, nullable=True)
        pt17 = Column(DOUBLE, nullable=True)
        pt18 = Column(DOUBLE, nullable=True)
        pt19 = Column(DOUBLE, nullable=True)
        pt20 = Column(DOUBLE, nullable=True)
        pt21 = Column(DOUBLE, nullable=True)
        pt22 = Column(DOUBLE, nullable=True)
        pt23 = Column(DOUBLE, nullable=True)
        pt24 = Column(DOUBLE, nullable=True)
        pt25 = Column(DOUBLE, nullable=True)
        pt26 = Column(DOUBLE, nullable=True)
        pt27 = Column(DOUBLE, nullable=True)
        pt28 = Column(DOUBLE, nullable=True)
        pt29 = Column(DOUBLE, nullable=True)
        pt30 = Column(DOUBLE, nullable=True)
        pt31 = Column(DOUBLE, nullable=True)
        pt32 = Column(DOUBLE, nullable=True)
        pt33 = Column(DOUBLE, nullable=True)
        pt34 = Column(DOUBLE, nullable=True)
        pt35 = Column(DOUBLE, nullable=True)
        pt36 = Column(DOUBLE, nullable=True)
        pt37 = Column(DOUBLE, nullable=True)
        pt38 = Column(DOUBLE, nullable=True)
        pt39 = Column(DOUBLE, nullable=True)
        pt40 = Column(DOUBLE, nullable=True)
        pt41 = Column(DOUBLE, nullable=True)
        pt42 = Column(DOUBLE, nullable=True)
        pt43 = Column(DOUBLE, nullable=True)
        pt44 = Column(DOUBLE, nullable=True)
        pt45 = Column(DOUBLE, nullable=True)
        pt46 = Column(DOUBLE, nullable=True)
        pt47 = Column(DOUBLE, nullable=True)
        pt48 = Column(DOUBLE, nullable=True)
        pt49 = Column(DOUBLE, nullable=True)
        pt50 = Column(DOUBLE, nullable=True)
        pt51 = Column(DOUBLE, nullable=True)
        pt52 = Column(DOUBLE, nullable=True)
        pt53 = Column(DOUBLE, nullable=True)
        pt54 = Column(DOUBLE, nullable=True)
        pt55 = Column(DOUBLE, nullable=True)
        pt56 = Column(DOUBLE, nullable=True)
        pt57 = Column(DOUBLE, nullable=True)
        pt58 = Column(DOUBLE, nullable=True)
        pt59 = Column(DOUBLE, nullable=True)
        pt60 = Column(DOUBLE, nullable=True)
        pt61 = Column(DOUBLE, nullable=True)
        pt62 = Column(DOUBLE, nullable=True)
        device = relationship("Device_list")
    DynamicTable.__table__.create(engine)