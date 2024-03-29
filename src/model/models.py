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

# from config import Config
# from libcom import path_directory_relative

# path=path_directory_relative("ipc_api") # name of project
# sys.path.append(path)
# # 
# database_hostname =Config.DATABASE_HOSTNAME
# database_port = Config.DATABASE_PORT
# database_password =Config.DATABASE_PASSWORD
# database_name =Config.DATABASE_NAME
# database_username =Config.DATABASE_USERNAME

# SQLALCHEMY_DATABASE_URL = f'mysql+pymysql://{database_username}:{database_password}@{database_hostname}:{database_port}/{database_name}'

# # connection_string="sqlite:///"+os.path.join(BASE_DIR,'site.db')

# engine=create_engine(SQLALCHEMY_DATABASE_URL,echo=False)
# Session=sessionmaker()
# Base=declarative_base()

# 
# class Page(Base):
#     __tablename__ = "page"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)
# 
class Driver_list(Base):
    __tablename__ = "driver_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

# 
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

# class Language_list(Base):
#     __tablename__ = "language_list"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     status = Column(Boolean, nullable=False, default=True)
# # 
class Device_type(Base):
    __tablename__ = "device_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    # 
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
# # 
# class Project_setup(Base):
#     __tablename__ = "project_setup"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     location = Column(String(255), nullable=True)
#     description = Column(String(255), nullable=True)
#     administrative_contact = Column(String(255), nullable=True)

#     id_first_page_on_login = Column(Integer, ForeignKey(
#         "page.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     id_logging_interval = Column(Integer, ForeignKey(
#         "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

#     id_scheduled_upload_time = Column(Integer, ForeignKey(
#         "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     number_times_retry = Column(Integer, nullable=False, default=3)
#     id_time_wait_before_retry = Column(Integer, ForeignKey(
#         "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     id_upload_debug_information = Column(Integer, ForeignKey(
#         "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

#     enable_upload_data_on_alarm_status = Column(
#         Boolean, nullable=False, default=True)
#     enable_upload_data_on_low_disk = Column(
#         Boolean, nullable=False, default=True)
#     enable_upload_data_on_system_startup = Column(
#         Boolean, nullable=False, default=True)
#     link_remote_access = Column(String(255), nullable=True)
#     allow_remote_access = Column(Boolean, nullable=False, default=False)
#     enable_static_routing = Column(Boolean, nullable=False, default=False)

#     id_time_zone = Column(Integer, ForeignKey(
#         "time_zone.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     Time1cycle = Column(DOUBLE(), nullable=False, default=5)
#     sampling_time1cycle = Column(DOUBLE(), nullable=False, default=15)

#     enable_zero_export = Column(Boolean, nullable=False, default=False)
#     value_zero_export = Column(DOUBLE(), nullable=False, default=100)

#     enable_limit_energy = Column(Boolean, nullable=False, default=False)
#     value_limit_energy = Column(DOUBLE(), nullable=False, default=100)

#     modhopper1 = Column(Integer, nullable=True)
#     modhopper2 = Column(Integer, nullable=True)
#     modhopper_key = Column(String(255), nullable=True)
#     modhopper_rf_config = Column(Integer, nullable=True)
#     modhopper_rf_channel = Column(Integer, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)
#     enable_search_modbus_rtu_device= Column(Boolean, nullable=False, default=True)
#     logging_interval  = relationship('Config_information', foreign_keys=[id_logging_interval])
#     first_page_on_login= relationship('Page', foreign_keys=[id_first_page_on_login])
#     enable_search_modbus_rtu_device= Column(Boolean, nullable=False, default=False)
#     number_limit_alarm= Column(Integer, nullable=True)
#     time_limit_alarm= Column(Integer, nullable=True)
#     mode_control = Column(Integer, nullable=False,default=0)
    
# class Template_library(Base):
#     __tablename__ = "template_library"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=True)
#     id_template_type = Column(Integer, ForeignKey(
#         "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     status = Column(Boolean, nullable=False, default=True)
    
#     device_group = relationship("Device_group", back_populates='templates_library')
#     point_list= relationship("Point_list", back_populates='template_library')
#     register_list= relationship("Register_block", back_populates='template_library')
# # 
# # 
class Pointclass_type(Base):
    __tablename__ = "pointclass_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
# 
# 
class Point_list(Base):
    __tablename__ = "point_list"
    id = Column(Integer, primary_key=True, nullable=False)
    # parent= Column(Integer, nullable=False)
    id_pointclass_type = Column(Integer, ForeignKey(
        "pointclass_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_pointkey = Column(Integer, nullable=False)
    id_template = Column(Integer, ForeignKey(
        "template_library.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    nameedit = Column(Boolean, nullable=False, default=True)
    id_type_units = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    unitsedit = Column(Boolean, nullable=False, default=True)
    
    id_pointtype = Column(Integer,  ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_config_information = Column(Integer,  ForeignKey(
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
    type_point= relationship('Config_information', foreign_keys=[id_pointtype])
    type_class= relationship('Pointclass_type', foreign_keys=[id_pointclass_type])
    type_config_information= relationship('Config_information', foreign_keys=[id_config_information])
    
    # 
    template_library=relationship("Template_library", back_populates='point_list')
    # # 
    # alarmenabled= Column(Boolean, nullable=False, default=True)
    # alarmsetpoint= Column(String(255), nullable=True)
    # id_alarmcodeerror= Column(Integer, ForeignKey(
    #     "error.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True)
    # id_alarmcondition= Column(Integer, ForeignKey(
    #     "config_information.id", ondelete="SET NULL", onupdate="SET NULL"), nullable=True)
    # 20/03/2024 
    parent =  Column(Integer ,ForeignKey("point_list.id"),nullable=False)  
    reply_to_point =relationship("Point_list",  remote_side=[parent]) 
class ManualPointList(Base):
    __tablename__ = "manual_point_list"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_type = Column(Integer, ForeignKey(
        "device_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_pointclass_type = Column(Integer, ForeignKey(
        "pointclass_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_pointkey = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    nameedit = Column(Boolean, nullable=False, default=True)
    id_type_units = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    unitsedit = Column(Boolean, nullable=False, default=True)
    
    id_pointtype = Column(Integer,  ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_config_information = Column(Integer,  ForeignKey(
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
    type_point= relationship('Config_information', foreign_keys=[id_pointtype])
    type_class= relationship('Pointclass_type', foreign_keys=[id_pointclass_type])
    type_config_information= relationship('Config_information', foreign_keys=[id_config_information])
    device_type = relationship('Device_type', foreign_keys=[id_device_type])
    
    parent =  Column(Integer, ForeignKey("point_list.id"), nullable=False)  
    reply_to_point =relationship("Point_list",  remote_side=[parent]) 
    
# # 
class Device_point_list_map(Base):
    __tablename__ = "device_point_list_map"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    low_alarm = Column(DOUBLE(), nullable=True, default=0)
    high_alarm = Column(DOUBLE(), nullable=True, default=0)
    id_device_list = Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_point_list = Column(Integer, ForeignKey(
        "point_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
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
# # 
# class Error_comparison(Base):
#     __tablename__ = "error_comparison"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(50), nullable=True)
#     description = Column(Text, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)


# class Error_level(Base):
#     __tablename__ = "error_level"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)


# class Error_type(Base):
#     __tablename__ = "error_type"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     status = Column(Boolean, nullable=False, default=True)


# class Alarm(Base):
#     __tablename__ = "alarm"
#     id = Column(BigInteger, primary_key=True, nullable=False)
#     id_device = Column(Integer, ForeignKey(
#         "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     id_error = Column(Integer, ForeignKey(
#         "error.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     enable = Column(Boolean, nullable=False, default=True)
#     opened =  Column(Boolean, nullable=False, default=False)
#     closed = Column(Boolean, nullable=False, default=False)
#     status = Column(Boolean, nullable=False, default=True)


# class Error(Base):
#     __tablename__ = "error"
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(255), nullable=True)
#     id_device_group = Column(Integer, ForeignKey(
#         "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     id_error_level = Column(Integer, ForeignKey(
#         "error_level.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     id_error_type = Column(Integer, ForeignKey(
#         "error_type.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     error_code = Column(String(255), nullable=False)
#     message = Column(String(255), nullable=False)
#     comparison = Column(String(255), nullable=True)
#     point = Column(String(255), nullable=False)
#     id_error_comparison = Column(Integer, ForeignKey(
#         "error_comparison.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
#     value = Column(DOUBLE, nullable=False, default=True)
#     enable = Column(Boolean, nullable=False, default=True)
#     status = Column(Boolean, nullable=False, default=True)
#     time_limit_alarm  = Column(Integer, nullable=False, default=5)
#     number_limit_alarm  = Column(Integer, nullable=False, default=5)
class Sync_data(Base):
    __tablename__ = "sync_data"
    id = Column(TIMESTAMP(timezone=True), primary_key=True,
                        nullable=False)
    synced= Column(Boolean, nullable=True, default=False)
    data=Column(String(255), nullable=True)
    id_upload_channel=Column(Integer, ForeignKey(
        "upload_channel.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_device=Column(Integer, ForeignKey(
        "device_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    modbusport= Column(Integer, nullable=True, default=0)
    modbusdevice= Column(Integer, nullable=True, default=0)
    ensuredir=Column(String(255), nullable=True)
    source=Column(String(255), nullable=True)
    filename=Column(String(255), nullable=True)
    deletedfile= Column(Boolean, nullable=True, default=True)
    createtime= Column(TIMESTAMP(timezone=True), 
                        nullable=True)
    updatetime= Column(TIMESTAMP(timezone=True), 
                        nullable=True)
    error=Column(String(255), nullable=True)
    number_of_time_retry= Column(Integer, nullable=False, default=0)
    status= Column(Boolean, nullable=False, default=True)
# #
# # 
# def create_table(table_name):
#     class DynamicTable(Base):
#         __tablename__ = table_name
#         id = Column(Integer, primary_key=True, autoincrement=True)
#         column_1 = Column(String(200))
#         column_2 = Column(String(200))

#     DynamicTable.__table__.create(engine)
def create_table_device(table_name):
    class DynamicTable(Base):
        __table_args__ = {'extend_existing': True} 
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
