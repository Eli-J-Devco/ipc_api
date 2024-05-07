from sqlalchemy import INTEGER, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .config import orm_provider as config


class PointList(config.Base):
    __tablename__ = "point_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    id_pointkey: Mapped[String] = mapped_column(String(255), unique=True)
    id_template: Mapped[int] = mapped_column(INTEGER, ForeignKey("template_library.id",
                                                                 ondelete="CASCADE",
                                                                 onupdate="CASCADE"),
                                             nullable=True)
    status: Mapped[int] = mapped_column(INTEGER, nullable=True)


class TemplateLibrary(config.Base):
    __tablename__ = "template_library"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)


class Devices(config.Base):
    __tablename__ = "device_list"

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, nullable=False)
    table_name: Mapped[str] = mapped_column(String(255), unique=True)
    view_table: Mapped[str] = mapped_column(String(255), unique=True)
    id_template: Mapped[int] = mapped_column(INTEGER, ForeignKey("template_library.id",
                                                                 ondelete="SET NULL",
                                                                 onupdate="SET NULL"),
                                             nullable=True)
