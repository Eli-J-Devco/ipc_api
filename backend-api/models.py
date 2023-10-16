from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base


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

class language_list(Base):
    __tablename__ = "language_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

class screen(Base):
    __tablename__ = "screen"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class auth_role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class auth_user_role_map(Base):
    __tablename__ = "user_role_map"
    id_user = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    status = Column(Boolean, nullable=False, default=True)

class auth_role_screen_map(Base):
    __tablename__ = "role_screen_map"
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_screen = Column(Integer, ForeignKey(
        "screen.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    auths = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class time_zone(Base):
    __tablename__ = "time_zone"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    namekey = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

class config_information(Base):
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

class config_type(Base):
    __tablename__ = "config_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

class access_level_whitelist(Base):
    __tablename__ = "access_level_whitelist"
    id = Column(Integer, primary_key=True, nullable=False)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=False)
    ip = Column(String(255), nullable=True)
    subnet = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class network_access(Base):
    __tablename__ = "network_access"
    id = Column(Integer, primary_key=True, nullable=False)
    id_ethernet = Column(Integer, ForeignKey(
        "ethernet.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_https = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_http = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_ssh_scp_rsync = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_telnet = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_ftp = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_type_modbus_tcp = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

class ethernet(Base):
    __tablename__ = "ethernet"
    id = Column(Integer, primary_key=True, nullable=False)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    id_type_ethernet = Column(Integer, ForeignKey(
        "config_information.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    allow_dns = Column(Boolean, nullable=True, default=False)
    ip_address = Column(String(255), nullable=True)
    subnet_mask = Column(String(255), nullable=True)
    mtu = Column(String(255), nullable=True)
    dns1 = Column(String(255), nullable=True)
    dns2 = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class static_routes(Base):
    __tablename__ = "static_routes"
    id = Column(Integer, primary_key=True, nullable=False)
    id_ethernet = Column(Integer, ForeignKey(
        "ethernet.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    entry_enable = Column(Boolean, nullable=False, default=False)
    destination = Column(String(255), nullable=True)
    subnet_mask = Column(String(255), nullable=True)
    gateway = Column(String(255), nullable=True)
    metric = Column(Integer, nullable=False, default=5)
    status = Column(Boolean, nullable=False, default=True)

class project_setup(Base):
    __tablename__ = "project_setup"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    administrative_contact = Column(String(255), nullable=True)

    id_first_page_on_login = Column(Integer, ForeignKey(
        "page.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    logging_interval = Column(Integer, nullable=False)

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

class error_comparison(Base):
    __tablename__ = "error_comparison"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class error_level(Base):
    __tablename__ = "error_level"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class error_type(Base):
    __tablename__ = "error_type"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

class alarm(Base):
    __tablename__ = "alarm"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device = Column(Integer, ForeignKey(
        "device.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    id_error = Column(Integer, ForeignKey(
        "error.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    opened = Column(String(255), nullable=False)
    closed = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

class error(Base):
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

class sync_data(Base):
    __tablename__ = "sync_data"
    id = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    id_device = Column(Integer, ForeignKey(
        "device.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    modbusport = Column(Integer, nullable=True)
    modbusdevice = Column(Integer, nullable=True)
    ensuredir = Column(String(255), nullable=True)
    source = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=True)
    synced = Column(Boolean, nullable=True, default=True)
    deletedfile = Column(Boolean, nullable=True, default=True)
    createtime = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    updatetime = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    data = Column(String(255), nullable=True)
    id_upload_chanel = Column(Integer, ForeignKey(
        "upload_chanel.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    error = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=True, default=True)

class upload_chanel(Base):
    __tablename__ = "upload_chanel"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=True)
    id_type_protocol = Column(Integer, ForeignKey(
        "type_protocol.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    uploadurl = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    selected_upload = Column(String(255), nullable=True)
    id_type_logging_interval = Column(Integer, ForeignKey(
        "type_logging_interval.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=True)
    allow_remote_configuration = Column(Boolean, nullable=False, default=True)
    status = Column(Boolean, nullable=False, default=True)

class datalog_inv1(Base):
    __tablename__ = "datalog_inv1"
    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    id_device = Column(Integer, ForeignKey(
        "device.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
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

class driver_list(Base):
    __tablename__ = "driver_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)

    
    




    
