from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DOUBLE
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
# from sqlalchemy.dialect.mysql import BOOLEAN
from database import Base


class upload_chanel(Base):
    __tablename__ = "upload_chanel"
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
