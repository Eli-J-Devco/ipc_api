# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import os
import sys
import warnings
from datetime import datetime

# with warnings.catch_warnings():
#     warnings.simplefilter("ignore", category=sa_exc.SAWarning)
from sqlalchemy import (
    DOUBLE,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import (
    Mapped,
    declarative_base,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.schema import CreateTable, DropTable
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

sys.path.append(
    (
        lambda project_name: (
            os.path.dirname(__file__)[
                : len(project_name) + os.path.dirname(__file__).find(project_name)
            ]
            if project_name and project_name in os.path.dirname(__file__)
            else -1
        )
    )("src")
)
# from sqlalchemy_utils.view import CreateView

# from sqlalchemy.orm.context import _ColumnEntity
# from sqlalchemy_views import CreateView, DropView

import warnings

# from sqlalchemy_utils.compat import _select_args
# from sqlalchemy_utils.view import CreateView
from sqlalchemy import Table
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import ClauseElement, Executable

from database.db import Base, engine

warnings.filterwarnings(
    "ignore", ".*Class SelectOfScalar will not make use of SQL compilation caching.*"
)


class Device_list(Base):
    __tablename__ = "device_list"
    id = Column(Integer, primary_key=True, nullable=False)
    table_name = Column(String(255), nullable=False)
    view_table = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    device_virtual = Column(Boolean, nullable=True, default=True)
    id_project_setup = Column(
        Integer,
        ForeignKey("project_setup.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_device_type = Column(
        Integer,
        ForeignKey("device_type.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_communication = Column(
        Integer,
        ForeignKey("communication.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    # 12/03/2024
    # id_device_group = Column(Integer, ForeignKey(
    #     "device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    id_template = Column(
        Integer,
        ForeignKey("template_library.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    rtu_bus_address = Column(Integer, nullable=True)
    tcp_gateway_ip = Column(String(255), nullable=True)
    tcp_gateway_port = Column(Integer, nullable=True)
    enable = Column(Boolean, nullable=True, default=True)

    max_watt = Column(DOUBLE, nullable=True)
    min_watt_in_percent = Column(DOUBLE, nullable=True)
    compensate_watt_factor = Column(DOUBLE, nullable=True)
    battery_mode = Column(Boolean, nullable=True, default=True)
    battery_normal_watt = Column(DOUBLE, nullable=True)
    battery_reduce_watt = Column(DOUBLE, nullable=True)
    battery_threshold_off_limit_in_v = Column(DOUBLE, nullable=True)
    battery_threshold_reduce_limit_in_v = Column(DOUBLE, nullable=True)
    battery_threshold_normal_limit_in_v = Column(DOUBLE, nullable=True)
    battery_threshold_on_limit_in_v = Column(DOUBLE, nullable=True)
    battery_priority = Column(Integer, nullable=True)

    point = Column(Integer, nullable=True)
    pv = Column(Integer, nullable=True)
    model = Column(Integer, nullable=True)
    function = Column(Integer, nullable=True)
    point_p = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="SET NULL", onupdate="SET NULL"),
        nullable=True,
    )  # id
    value_p = Column(DOUBLE, nullable=True)
    send_p = Column(Boolean, nullable=True, default=True)
    point_q = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="SET NULL", onupdate="SET NULL"),
        nullable=True,
    )  # id
    value_q = Column(DOUBLE, nullable=True)
    send_q = Column(Boolean, nullable=True, default=True)
    point_pf = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="SET NULL", onupdate="SET NULL"),
        nullable=True,
    )  # id
    value_pf = Column(DOUBLE, nullable=True)
    send_pf = Column(Boolean, nullable=True, default=True)
    max = Column(DOUBLE, nullable=True)
    allow_error = Column(DOUBLE, nullable=True)
    enable_poweroff = Column(Boolean, nullable=True, default=True)
    inverter_shutdown = Column(TIMESTAMP(timezone=True), nullable=True)
    status = Column(Boolean, nullable=True, default=True)

    #
    communication = relationship("Communication", foreign_keys=[id_communication])
    # point_p_list = relationship('Point_list', foreign_keys=[point_p])
    # point_q_list  = relationship('Point_list', foreign_keys=[point_q])
    # point_pf_list  = relationship('Point_list', foreign_keys=[point_pf])
    #
    # # device_group  = relationship('Device_group', foreign_keys=[id_device_group])
    # 12/03/2024
    # device_group= relationship("Device_group", back_populates="device_list")
    device_type = relationship("Device_type", foreign_keys=[id_device_type])
    mode = Column(Integer, nullable=True, default=False)


class Device_mppt(Base):
    __tablename__ = "device_mppt"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_list = Column(
        Integer,
        ForeignKey("device_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_point_list = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=True)
    voltage = Column(DOUBLE, nullable=True)
    current = Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_list = relationship("Device_list", foreign_keys=[id_device_list])


class Device_mppt_string(Base):
    __tablename__ = "device_mppt_string"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_mppt = Column(
        Integer,
        ForeignKey("device_mppt.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_device_list = Column(
        Integer,
        ForeignKey("device_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_point_list = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    name = Column(String(255), nullable=True)
    namekey = Column(String(255), nullable=True)
    panel = Column(Integer, nullable=True)
    current = Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_mptt = relationship("Device_mppt", foreign_keys=[id_device_mppt])
    device_list = relationship("Device_list", foreign_keys=[id_device_list])
    point_list = relationship("Point_list", foreign_keys=[id_point_list])


class Device_panel(Base):
    __tablename__ = "device_panel"
    id = Column(Integer, primary_key=True, nullable=False)
    id_device_string = Column(
        Integer,
        ForeignKey("device_mppt_string.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_device_list = Column(
        Integer,
        ForeignKey("device_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    id_point_list = Column(
        Integer,
        ForeignKey("point_list.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    name = Column(String(255), nullable=True)
    serial_number = Column(String(255), nullable=True)
    pmax = Column(DOUBLE, nullable=True)
    vmpp = Column(DOUBLE, nullable=True)
    impp = Column(DOUBLE, nullable=True)
    voc = Column(DOUBLE, nullable=True)
    isc = Column(DOUBLE, nullable=True)
    weight = Column(DOUBLE, nullable=True)
    status = Column(Boolean, nullable=True, default=True)
    device_mppt_string = relationship(
        "Device_mppt_string", foreign_keys=[id_device_string]
    )


class Data_panel(Base):
    __tablename__ = "data_panel"
    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=True)
    id_device_panel = Column(
        Integer,
        ForeignKey("device_panel.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )

    device_panel = relationship("Device_panel", foreign_keys=[id_device_panel])


class CreateView(Executable, ClauseElement):
    def __init__(self, name, select):
        self.name = name
        self.select = select


@compiles(CreateView)
def visit_create_view(element, compiler, **kw):
    return "CREATE VIEW %s AS %s" % (
        element.name,
        compiler.process(element.select, literal_binds=True),
    )


def create_table_device(table_name, pointList=[]):
    # TABLE_SPEC = [
    #                 ('id', Integer),
    #                 ('name', String(255)),
    #                 ('time',DateTime),
    #                 ('whatever', String(255)),
    #                 ("employee_dept", Integer,ForeignKey(
    #     "point_list.id", ondelete="SET NULL", onupdate="SET NULL"))
    #             ]

    # TABLE_NAME = 'sample_table'

    # columns = [Column(n, t,t1) for n, t,t1 in TABLE_SPEC]
    # table = Table(TABLE_NAME, MetaData(), *columns)
    meta = MetaData()

    new_table_device = Table(
        table_name,
        meta,
        Column("time", TIMESTAMP(timezone=True), primary_key=True, nullable=False),
        Column("id_device", Integer, ForeignKey(Device_list.id)),
        Column("error", Integer, nullable=True),
        Column("low_alarm", Integer, nullable=True),
        Column("high_alarm", Integer, nullable=True),
        Column("serial_number", String(255), nullable=True),
    )
    for i, item in enumerate(pointList):
        new_table_device.append_column(Column(str(item["name"]), DOUBLE, nullable=True))
    # table_creation_sql = CreateTable(new_table_device)
    # return new_table_device.create(engine)
    return new_table_device


def create_table(tbl_name, number=10):
    print("create_table")

    class CreateTables(Base):
        __table_args__ = {"extend_existing": True}
        __tablename__ = f"{tbl_name}"
        time: Mapped[TIMESTAMP] = mapped_column(
            TIMESTAMP(timezone=True), primary_key=True, nullable=False
        )
        # id_device: Mapped[str] = mapped_column(Integer, ForeignKey(
        #     Device_list.id, ondelete="SET NULL", onupdate="SET NULL"), nullable=True)
        # error = Column(Integer, nullable=True)
        # low_alarm = Column(Integer, nullable=True)
        # high_alarm = Column(Integer, nullable=True)
        # serial_number = Column(String(255), nullable=True)

    tbl = CreateTables.__table__
    for col in range(number):
        tbl._columns.add(Column(f"pt{col}", Integer))
    result = CreateTable(tbl)
    return tbl
    # return CreateTable.__table__
