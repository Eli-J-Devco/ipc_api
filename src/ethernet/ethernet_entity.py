from ..config import config
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Ethernet(config.Base):
    __tablename__ = "ethernet"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id_project_setup: Mapped[int] = mapped_column(Integer,
                                                  ForeignKey("project_setup.id",
                                                             ondelete="CASCADE",
                                                             onupdate="CASCADE"),
                                                  nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    namekey: Mapped[str] = mapped_column(String, primary_key=True, unique=True, nullable=False)
    id_type_ethernet: Mapped[int] = mapped_column(Integer,
                                                  ForeignKey("config_information.id",
                                                             ondelete="CASCADE",
                                                             onupdate="CASCADE"),
                                                  nullable=False)
    allow_dns: Mapped[bool] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    subnet_mask: Mapped[str] = mapped_column(String, nullable=True)
    gateway: Mapped[str] = mapped_column(String, nullable=True)
    mtu: Mapped[str] = mapped_column(String, nullable=True)
    dns1: Mapped[str] = mapped_column(String, nullable=True)
    dns2: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[bool] = mapped_column(Integer, nullable=False)

    project_setup = relationship("ProjectSetup", foreign_keys=[id_project_setup])
    type_ethernet = relationship("ConfigInformation", foreign_keys=[id_type_ethernet])


