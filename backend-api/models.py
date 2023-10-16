from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base

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
    # is_active = Column(Boolean, nullable=False, default=False)
    # status = Column(Boolean, nullable=False, default=True)


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
    id = Column(Integer, primary_key=True, nullable=False)
    id_project_setup = Column(Integer, ForeignKey(
        "project_setup.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    enable = Column(Boolean, nullable=False, default=False)
    ip = Column(String(255), nullable=True)
    subnet = Column(String(255), nullable=True)
    status = Column(Boolean, nullable=False, default=True)


class network_access(Base):
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
    enable_upload_data_on_alarm_status = Column(
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


# class error_comparison(Base):
# class error_level(Base):
# class error_type(Base):
# class alarm(Base):
# class error(Base):
