from src.config import config
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Template(config.Base):
    __tablename__ = "template_library"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    id_device_group: Mapped[int] = mapped_column(Integer, ForeignKey("device_group.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    status: Mapped[int] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(String, nullable=True)

    point_list = relationship("Point", back_populates="template_library")
    # register_list = relationship("RegisterBlock", back_populates="template_library")
    device_group = relationship("DeviceGroup", foreign_keys=[id_device_group])


