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


class Screen(Base):
    __tablename__ = "screen"
    id = Column(Integer, primary_key=True, nullable=False)
    screen_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    class_icon= Column(String(255), nullable=False)
    level= Column(Integer, nullable=True)
    parent= Column(Integer, nullable=True)
    path= Column(String(200), nullable=True)
    has_child= Column(Boolean, nullable=False, default=False)
    created_date=Column(TIMESTAMP(timezone=True),
                        nullable=True)
    created_by = Column(String(255), nullable=True)
    updated_date=Column(TIMESTAMP(timezone=True),
                        nullable=True)
    updated_by = Column(String(255), nullable=True)
    show_menu= Column(Boolean, nullable=False, default=True)
    

class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    role_map=relationship("Role_screen_map", back_populates='role')
    
class Role_screen_map(Base):
    __tablename__ = "role_screen_map"
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_screen = Column(Integer, ForeignKey(
        "screen.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    auths = Column(Integer, nullable=True)
    status = Column(Boolean, nullable=False, default=True)

    ## role  = relationship('Role', foreign_keys=[id_role])
    screen  = relationship('Screen', foreign_keys=[id_screen])
    
    role=relationship("Role", back_populates='role_map')
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    # fullname = Column(String(255), nullable=True)
    
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    salt = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    status = Column(Boolean, nullable=False, default=True)
    
    create_date = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    
    last_login = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    create_by = Column(String(200), nullable=False)
    
    updated_date = Column(TIMESTAMP(timezone=True),
                        nullable=True)
    updated_by = Column(String(200), nullable=False)
    
    # date_joined = Column(TIMESTAMP(timezone=True),
                        # nullable=True)
    # id_language = Column(Integer, ForeignKey(
    #     "language_list.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    # is_active = Column(Boolean, nullable=False, default=False)
    
    # language  = relationship('Language_list', foreign_keys=[id_language])
    
    
class User_role_map(Base):
    __tablename__ = "user_role_map"
    id_user = Column(Integer, ForeignKey(
        "user.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    id_role = Column(Integer, ForeignKey(
        "role.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    
    status = Column(Boolean, nullable=False, default=True)
    ## user  = relationship('User', foreign_keys=[id_user])
    ## role  = relationship('Role', foreign_keys=[id_role])
    ## role_screen=relationship("Role_screen_map", back_populates='user_role')
    user  = relationship('User')
    role  = relationship('Role')
    
    
    
    # id_user = mapped_column(ForeignKey("user.id"), primary_key=True)
    # id_role = mapped_column(ForeignKey("role.id"), primary_key=True)
