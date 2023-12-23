# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
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
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    result_user_role = db.query(models.User_role_map).filter(
        models.User_role_map.id_user == user.id).all()
    
    # print(f'result_role: {result_user_role.role.__dict__}')
    if not result_user_role:
       raise HTTPException(status_code=404, detail="Role map not found")
    auth_list=[]
   
    role_list=[]
    for item in result_user_role:
        new_item={
            "id": item.role.id,
            "name": item.role.name,
            "description": item.role.description,
            "status": item.role.status,
        }
        new_role_screen=[]
        for item_role_screen in item.role.role_map:
            
        role_list.append(new_item)
    for item_role in result_user_role:
        # print(f'result_user: {item.__dict__}')
        # print(f'result_role: {item.role.__dict__}')
        # print(f'result_role_map: {item.role.role_map[0].__dict__}')
        if hasattr(item_role.role, 'role_map'):
            for item_role_screen in item_role.role.role_map:
                if hasattr(item_role_screen, 'auths'):
                    auth_list.append(item_role_screen.auths)
    result_auth=convert_binary_auth(auth_list)
    # get all screen
    result_screen= db.query(models.Screen).all()
    if not result_screen:
       raise HTTPException(status_code=404, detail="Screen list empty")
    result_user=schemas.UserLoginOut(
        fullname=user.fullname,
        phone=user.phone,
        id_language=user.id_language,
        auth=result_auth
    )
    # refresh a token
    refresh_token= oauth2.create_refresh_token(data={"user_id": user.id})
    # create a token
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    # return token
    
    return {"refresh_token": refresh_token,
            "access_token": access_token, 
            "token_type": "bearer",
            "user":result_user,
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
