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
from utils.logger_manager import setup_logger

LOGGER = setup_logger(module_name='API')
SECRET_KEY = Config.SECRET_KEY
REFRESH_SECRET_KEY = Config.SECRET_KEY 
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES= Config.REFRESH_TOKEN_EXPIRE_MINUTES
PASSWORD_SECRET_KEY= Config.PASSWORD_SECRET_KEY 
router = APIRouter(tags=['Authentication'])

# from api.domain.user import models as user_models
# from api.domain.user import models, schemas

import api.domain.user.models as user_models
import api.domain.user.schemas as user_schemas
from utils import oauth2
from utils.passwordHasher import convert_binary_auth, decrypt, encrypt, verify


# Describe functions before writing code
# /**
# 	 * @description get device list
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_credentials,db}
# 	 * @return data (Token)
# 	 */ 
@router.post('/login/', response_model=user_schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        
        # username b'U2FsdGVkX185D6fXTKLAUMsaWnIm0861YAMQXtNE5/V1RPChpxkWIAYlA05RJmio'
        # password b'U2FsdGVkX19pC80uku9GJZDYOO2ElN06ELaZdw514v8='
        # pprint(user_credentials.username)
        # pprint(user_credentials.password)
        username=(decrypt(user_credentials.username, PASSWORD_SECRET_KEY.encode())).decode()
        password=(decrypt(user_credentials.password, PASSWORD_SECRET_KEY.encode())).decode()
        # pprint(f'username: {username}')
        # pprint(f'pass: {password}')
        user_query = db.query(user_models.User).filter(
            user_models.User.email == username)
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
        
        result_user_role = db.query(user_models.User_role_map).filter(
            user_models.User_role_map.id_user == result_user.id).all()
        
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
        screen_list=[]
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
                        screen_list.append(new_item_role_screen)
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
        # print(f'auth_list: {auth_list}')
        result_auth=convert_binary_auth(auth_list)
        
        id_screen_list = [x["id"] for i, x in enumerate(screen_list) if x['id'] not in {y['id'] for y in screen_list[:i]}]
        # id_screen_list = [item["id"] for item in screen_list ]
        # print(f'screen_list: {screen_list}')
        # get all screen
        # result_screen= db.query(user_models.Screen).all()
        # if not result_screen:
        #     return JSONResponse(
        #                 status_code=status.HTTP_403_FORBIDDEN, 
        #                 content={"detail": "Screen list empty"}
        #                 )
        
        
        info_user_out=user_schemas.UserLoginOut(
            first_name=result_user.first_name,
            last_name=result_user.last_name,
            email=result_user.email,
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
        # LOGGER.info(f"--- Login: {user_credentials.username} ---")
        role_screen={}
        screen_list=[]
        for role_item in role_list:
            for screen_item in role_item["screen"]:
                screen_list.append(screen_item)
                if screen_item["id"] in id_screen_list:
                    id_role="id"+str(screen_item["id"])
                    if str(id_role) in role_screen.keys():
                        auth=[]
                        auth=role_screen[id_role]["auth"]
                        auth.append(screen_item["auth"])
                        role_screen[id_role]={
                        "id":screen_item["id"],
                        "auth":auth
                        }
                    else:
                        role_screen[id_role]={
                        "id":screen_item["id"],
                        "auth":[screen_item["auth"]]
                        }
        new_Data = [x for i, x in enumerate(screen_list) if x['id'] not in {y['id'] for y in screen_list[:i]}]
        # print(new_Data)
        new_role_screen=[]
        for item in new_Data:
            new_item={
            "id":item["id"],
            "name":item["name"],
            "description":item["description"],
            "auth":convert_binary_auth(role_screen["id"+str(item["id"])]["auth"]),
            }
            new_role_screen.append(new_item)

        # print(f'new_role_screen: {new_role_screen}')
        return {"refresh_token": refresh_token,
                "access_token": access_token, 
                "token_type": "bearer",
                # "user":info_user_out,
                # "screen":result_screen,#s
                # "role":role_list #s
                "first_name":info_user_out.first_name,
                "last_name":info_user_out.last_name,
                "email":info_user_out.email,
                "permissions":new_role_screen
                
                }
    except (Exception) as err:
        print('Error : ',err.__class__)
        # print('Errors : ',err)
        LOGGER.error(f'--- {err} ---')
        return JSONResponse(content={"detail": "Internal Server Error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
# Describe functions before writing code
# /**
# 	 * @description refresh token
# 	 * @author vnguyen
# 	 * @since 17-12-2023
# 	 * @param {TokenItem,db}
# 	 * @return data (Token)
# 	 */ 
@router.post("/refresh_token/", response_model=user_schemas.Token)
def refresh_token(request: user_schemas.TokenItem, db: Session = Depends(get_db)):
    refresh_token = request.refresh_token
    # print(f'refresh_token: {refresh_token}')
    credentials_exception = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                        
                                        content={"detail": "Could not validate credentials"},
                                        headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(refresh_token,SECRET_KEY, algorithms=[ALGORITHM])
        print(f'payload: {payload}')
        
        access_token = oauth2.create_access_token(data={"user_id": payload["user_id"]})
        id=payload["user_id"]
        user_query = db.query(user_models.User).filter(user_models.User.id == id)
        user = user_query.first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN, 
                content={"detail": "Invalid Credentials"}
                )
        return {"refresh_token": refresh_token,
                "access_token": access_token, 
                "token_type": "bearer"}
    # except JWTError:
    except (Exception) as err:
        print('Error : ',err.__class__)
        LOGGER.error(f'--- {err} ---')
        raise credentials_exception    
