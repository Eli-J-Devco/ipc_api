# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# import os
import sys
from datetime import datetime, timedelta

import database
# from . import schemas, database, models
import models
import schemas
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

# from pathlib import Path


# sys.path.insert(1, "D:/NEXTWAVE/project/ipc_api")
# from config import settings
sys.path.insert(1, "../")
from config import Config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


# SECRET_KEY
# Algorithm
# Expriation time

# SECRET_KEY = settings.secret_key
# ALGORITHM = settings.algorithm
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
#
# load_dotenv(dotenv_path=Path("../.env"))
# SECRET_KEY = os.getenv('SECRET_KEY')
# ALGORITHM = os.getenv('ALGORITHM')
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
#
SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):

    try:
        print(f'SECRET_KEY:  {SECRET_KEY}')
        print(f'token:  {token}')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'payload:  {payload}')
        id: str = payload.get("user_id")
        print(f'id:  {id}')
        if id is None:
            raise credentials_exception
        print(f'if :  {id}')
        token_data = schemas.TokenData(id=str(id))
        print(f'token_data:  {token_data}')
    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    print("++++++++++++++++++++++++++++++++++++++++")
    # print(f'token:  {token}')
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    print(f'token get_current_user:  {token}')
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
