# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import sys
from pprint import pprint

import database
import models
import oauth2
import schemas
import utils
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import text
from sqlalchemy.orm import Session

sys.path.insert(1, "../")
from config import Config

SECRET_KEY = Config.SECRET_KEY
REFRESH_SECRET_KEY = Config.SECRET_KEY
ALGORITHM = Config.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES= Config.REFRESH_TOKEN_EXPIRE_MINUTES
router = APIRouter(tags=['Authentication'])
from utils import convert_binary_auth


# Describe functions before writing code
# /**
# 	 * @description get device list
# 	 * @author vnguyen
# 	 * @since 30-11-2023
# 	 * @param {user_credentials,db}
# 	 * @return data (Token)
# 	 */ 
@router.post('/login/', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    pprint(user_credentials.username)
    user_query = db.query(models.User).filter(
        models.User.email == user_credentials.username)
    result_user=user_query.first()

    if not result_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    now = datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    user_query.update(dict( 
                            last_login=now,    
                           ), synchronize_session=False)
    db.commit()
    if not utils.verify(user_credentials.password, result_user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    result_user_role = db.query(models.User_role_map).filter(
        models.User_role_map.id_user == result_user.id).all()
    
    # print(f'result_role: {result_user_role.role.__dict__}')
    if not result_user_role:
       raise HTTPException(status_code=404, detail="Role map not found")
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
        raise HTTPException(status_code=404, detail="Screen list empty")
    result_user_out=schemas.UserLoginOut(
        fullname=result_user.fullname,
        phone=result_user.phone,
        id_language=result_user.id_language,
        auth=result_auth
    )
    # refresh a token
    refresh_token= oauth2.create_refresh_token(data={"user_id": result_user.id})
    # create a token
    access_token = oauth2.create_access_token(data={"user_id": result_user.id})
    # return token
    
    return {"refresh_token": refresh_token,
            "access_token": access_token, 
            "token_type": "bearer",
            "user":result_user_out,
            "screen":result_screen,
            "role":role_list
            }
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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
        return {"refresh_token": refresh_token,
                "access_token": access_token, 
                "token_type": "bearer"}
    except JWTError:
        raise credentials_exception    
