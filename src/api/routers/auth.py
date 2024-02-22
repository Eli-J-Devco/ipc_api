# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import logging
import os
import sys
from pprint import pprint

# import oauth2
# import schemas
# import utils
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

# import models
# import database
sys.path.append((lambda project_name: os.path.dirname(__file__)[:len(project_name) + os.path.dirname(__file__).find(project_name)] if project_name and project_name in os.path.dirname(__file__) else -1)
                ("src"))

from configs.config import *
from database.db import get_db

SECRET_KEY = Config.SECRET_KEY
REFRESH_SECRET_KEY = Config.SECRET_KEY 
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES= Config.REFRESH_TOKEN_EXPIRE_MINUTES
PASSWORD_SECRET_KEY= Config.PASSWORD_SECRET_KEY 
router = APIRouter(tags=['Authentication'])

# from api.domain.user import models as user_models
from api.domain.user import models, schemas
from utils import oauth2
from utils.passwordHasher import convert_binary_auth, decrypt, encrypt, verify

LOGGER = logging.getLogger(__name__)

# Describe functions before writing code
# /**
# 	 * @description get device list
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_credentials,db}
# 	 * @return data (Token)
# 	 */ 
@router.post('/login/', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        # username b'U2FsdGVkX19ZDkZuu1l7LGxevbTdWIgvCUD9KE6dVVTgTFVhFvfxvxBrIR65e0aa'
        # password b'U2FsdGVkX18mv2nMwFhaD0yvWSFRmIzFrxbTaSMcWyI='
        pprint(user_credentials.username)
        pprint(user_credentials.password)
        username=(decrypt(user_credentials.username, PASSWORD_SECRET_KEY.encode())).decode()
        password=(decrypt(user_credentials.password, PASSWORD_SECRET_KEY.encode())).decode()
        pprint(f'username: {username}')
    
        user_query = db.query(models.User).filter(
            models.User.email == username)
        result_user=user_query.first()
        
        if not result_user:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"detail": "Invalid Credentials"}
                )
     
        now = datetime.datetime.now(
                datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        user_query.update(dict( 
                                last_login=now,    
                            ), synchronize_session=False)
        db.commit()
        if not verify(password, result_user.password):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"detail": "Invalid Credentials"}
                )
        
        result_user_role = db.query(models.User_role_map).filter(
            models.User_role_map.id_user == result_user.id).all()
        
        # print(f'result_role: {result_user_role.role.__dict__}')
        if not result_user_role:
            return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    content={"detail": "Role map not found"}
                    )
        auth_list=[]
        # [{'id': 1, 'name': 'Admin', 'description': None, 'status': True, 
        #   'screen': [{'id_role': 1, 'id_screen': 1, 'screen': 'Overview'}, {'id_role': 1, 'id_screen': 2, 'screen': 'Login'}, {'id_role': 1, 'id_screen': 3, 'screen': 'Quick Start'}]}, 
        #  {'id': 2, 'name': 'Manager', 'description': None, 'status': True, 
        #   'screen': [{'id_role': 2, 'id_screen': 1, 'screen': 'Overview'}]}]
        role_list=[]
        for item in result_user_role:

            new_role_screen=[]
            if hasattr(item.role, 'role_map'):
                for item_role_screen in item.role.role_map:
                    if hasattr(item_role_screen, 'screen'):
                        new_item_role_screen={
                            "id":item_role_screen.screen.id,
                            "name":item_role_screen.screen.name,
                            "description":item_role_screen.screen.description,
                            "status":item_role_screen.screen.status,
                            "auth":item_role_screen.auths
                        }
                        new_role_screen.append(new_item_role_screen)
            new_item={
                "id": item.role.id,
                "name": item.role.name,
                "description": item.role.description,
                "status": item.role.status,
                "screen":new_role_screen
                }
            role_list.append(new_item)
        for item_role in result_user_role:
            if hasattr(item_role.role, 'role_map'):
                for item_role_screen in item_role.role.role_map:
                    if hasattr(item_role_screen, 'auths'):
                        auth_list.append(item_role_screen.auths)
        result_auth=convert_binary_auth(auth_list)
        # get all screen
        result_screen= db.query(models.Screen).all()
        if not result_screen:
            return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN, 
                        content={"detail": "Screen list empty"}
                        )
        
        
        result_user_out=schemas.UserLoginOut(
            first_name=result_user.first_name,
            last_name=result_user.last_name,
            # fullname=result_user.fullname,
            phone=result_user.phone,
            # id_language=result_user.id_language,
            auth=result_auth
        )
        # refresh a token
        refresh_token= oauth2.create_refresh_token(data={"user_id": result_user.id})
        # create a token
        access_token = oauth2.create_access_token(data={"user_id": result_user.id})
        # return token
        LOGGER.info(f"--- Login: {user_credentials.username} ---")
        return {"refresh_token": refresh_token,
                "access_token": access_token, 
                "token_type": "bearer",
                "user":result_user_out,
                "screen":result_screen,
                "role":role_list
                }
    except (Exception) as err:
        # print('Error : ',err.__class__)
        print('Errors : ',err)
# Describe functions before writing code
# /**
# 	 * @description refresh token
# 	 * @author vnguyen
# 	 * @since 17-12-2023
# 	 * @param {TokenItem,db}
# 	 * @return data (Token)
# 	 */ 
@router.post("/refresh_token/", response_model=schemas.Token)
def refresh_token(request: schemas.TokenItem, db: Session = Depends(get_db)):
    refresh_token = request.refresh_token
    print(f'refresh_token: {refresh_token}')
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(refresh_token,SECRET_KEY, algorithms=[ALGORITHM])
        print(f'payload: {payload}')
        
        access_token = oauth2.create_access_token(data={"user_id": payload["user_id"]})
        id=payload["user_id"]
        user_query = db.query(models.User).filter(models.User.id == id)
        user = user_query.first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"detail": "Invalid Credentials"}
                )
        return {"refresh_token": refresh_token,
                "access_token": access_token, 
                "token_type": "bearer"}
    except JWTError:
        raise credentials_exception    
