# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
# import os
import os
import sys
from datetime import datetime, timedelta

# import schemas
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

sys.path.append( (lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))
from api.domain.user import models, schemas
from configs.config import Config
from database.db import get_db

# import database
# sys.path.insert(1, "../")
# from config import Config

# from . import schemas, database, models
# import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')



#
SECRET_KEY = Config.SECRET_KEY
REFRESH_SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES= Config.REFRESH_TOKEN_EXPIRE_MINUTES

# Describe functions before writing code
# /**
# 	 * @description create access token
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_id}
# 	 * @return data (encoded_jwt)
# 	 */
def create_access_token(data: dict):
   
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(minutes=eval(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

# Describe functions before writing code
# /**
# 	 * @description verify access token
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {token,credentials_exception}
# 	 * @return data (token_data)
# 	 */
def verify_access_token(token: str, credentials_exception):

    try:
        print('---------- verify_access_token ----------')
        print(f'SECRET_KEY:  {SECRET_KEY}')
        print(f'token:  {token}')
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'payload:  {payload}')
        id: str = payload.get("user_id")
        print(f'id:  {id}')
        if id is None:
            raise credentials_exception
        # print(f'if :  {id}')
        token_data = schemas.TokenData(id=str(id))
        # print(f'token_data:  {token_data}')
    except JWTError:
        raise credentials_exception

    return token_data

# Describe functions before writing code
# /**
# 	 * @description get current user
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {token,db}
# 	 * @return data (user)
# 	 */
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    print(f'token get_current_user:  {token}')
    print(f'token id:  {token.id}')
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
# Describe functions before writing code
# /**
# 	 * @description create refresh token
# 	 * @author vnguyen
# 	 * @since 17-12-2023
# 	 * @param {user_id}
# 	 * @return data (encoded_jwt)
# 	 */
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expires_delta = datetime.utcnow() + timedelta(minutes=eval(REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt