from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base


class driver_list(Base):
    __tablename__ = "driver_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)


class device_group(Base):
    __tablename__ = "device_group"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    id_template = Column(Integer, ForeignKey(
        "template.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class template_library(Base):
    __tablename__ = "template_library"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class device_type(Base):
    __tablename__ = "device_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class register_block(Base):
    __tablename__ = "register_block"
    id = Column(Integer, primary_key=True, nullable=False)
    id_template = Column(Integer, ForeignKey(
        "template.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    addr = Column(Integer, nullable=False)
    count = Column(Integer, nullable=False)
    id_type_function = Column(Integer, ForeignKey(
        "type_function.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)


class point_list(Base):
    __tablename__ = "point_list"
    id = Column(Integer, primary_key=True, nullable=False)
    id_pointkey = Column(Integer, nullable=False)
    id_template = Column(Integer, ForeignKey(
        "template.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    nameedit = Column(Boolean, nullable=False, default=True)
    id_type_units = Column(Integer, ForeignKey(
        "type_units.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    unitsedit = Column(Boolean, nullable=False, default=True)
    equaltion = Column(Boolean, nullable=False, default=True)
    config = Column(Integer, nullable=False)
    register = Column(Integer, nullable=False)
    id_type_datatype = Column(Integer, ForeignKey(
        "type_datatype.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_byteorder = Column(Integer, ForeignKey(
        "type_byteorder.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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


class communication(Base):
    __tablename__ = "communication"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
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


class device_list(Base):
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
    rtu_bus_adress = Column(Integer, nullable=True)
    tcp_gateway_ip = Column(String(255), nullable=True)
    tcp_gateway_port = Column(Integer, nullable=True)
    enable = Column(Boolean, nullable=True, default=True)
    point = Column(Integer, nullable=True)
    pv = Column(Integer, nullable=True)
    model = Column(Integer, nullable=True)
    funtion = Column(Integer, nullable=True)
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
    alow_error = Column(DOUBLE, nullable=True)
    enable_poweroff = Column(Boolean, nullable=True, default=True)
    inverter_shotdown = Column(TIMESTAMP(timezone=True),
                               nullable=True)
    status = Column(Boolean, nullable=True, default=True)
