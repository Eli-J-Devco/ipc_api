from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
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
    # is_active = Column(Boolean, nullable=False, default=False)
    # status = Column(Boolean, nullable=False, default=True)


class language_list(Base):
    __tablename__ = "language_list"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
