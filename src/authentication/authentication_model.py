# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
import datetime
import logging
from typing import Optional

from jose import jwt
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status

from ..security import SecurityRepository
from ..utils.utils import get_timedelta
from ..utils.password_hasher import decrypt, verify


class Authentication(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int = None


class Permission(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    auth: int


class AuthenticationResponse(BaseModel):
    first_name: str = None
    last_name: str = None
    email: str = None
    refresh_token: str = None
    access_token: str = None
    project_id: int = None
    permissions: list[Permission] = None


class AuthenticationConfig:
    def __init__(self, password_secret_key=None):
        self._oauth2_scheme = OAuth2PasswordBearer(tokenUrl='authentication/login')
        self._password_secret_key = password_secret_key
        self._security = SecurityRepository.get_security_config()

    def get_oauth2_scheme(self) -> OAuth2PasswordBearer:
        """
        Get the OAuth2 scheme
        :author nhan.tran:
        :date 20-05-2024:
        :return: OAuth2PasswordBearer
        """
        return self._oauth2_scheme

    def get_password_secret_key(self) -> str:
        """
        Get the password secret key
        :author nhan.tran:
        :date 20-05-2024:
        :return: str
        """
        return self._password_secret_key

    def set_password_secret_key(self, password_secret_key) -> None:
        self._password_secret_key = password_secret_key

    def decrypt_user_credential(self, user: Authentication) -> Authentication | HTTPException:
        """
        Decrypt the user credential
        :author nhan.tran:
        :date 20-05-2024:
        :param user:
        :return: Authentication | HTTPException
        """
        try:
            username = (decrypt(user.username, self.get_password_secret_key().encode())).decode()
            password = (decrypt(user.password, self.get_password_secret_key().encode())).decode()
            return Authentication(username=username, password=password)
        except Exception as e:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    def create_refresh_token(self, data: dict) -> str:
        """
        Create a refresh token
        :author nhan.tran:
        :date 20-05-2024:
        :param data:
        :return: str
        """
        to_encode = data.copy()
        value, unit = self._security.get_refresh_token_timeout()
        expire = datetime.datetime.utcnow() + get_timedelta(value, unit)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode,
                                 self._security.get_refresh_secret_key(),
                                 algorithm=self._security.get_algorithm())

        return encoded_jwt

    def create_access_token(self, data: dict) -> str:
        """
        Create an access token
        :author nhan.tran:
        :date 20-05-2024:
        :param data:
        :return: str
        """
        to_encode = data.copy()
        value, unit = self._security.get_access_token_timeout()
        expire = datetime.datetime.utcnow() + get_timedelta(value, unit)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, self._security.get_secret_key(), algorithm=self._security.get_algorithm())

        return encoded_jwt

    def verify_refresh_token(self, token, credentials_exception) -> TokenData | HTTPException:
        """
        Verify the refresh token
        :author nhan.tran:
        :date 20-05-2024:
        :param token:
        :param credentials_exception:
        :return: TokenData | HTTPException
        """
        try:
            payload = jwt.decode(token,
                                 self._security.get_refresh_secret_key(),
                                 algorithms=[self._security.get_algorithm()])
            user_id = payload.get("user_id")

            if user_id is None:
                raise credentials_exception

            token_data = TokenData(id=str(user_id))
            return token_data
        except jwt.ExpiredSignatureError:
            raise credentials_exception
        except jwt.JWTError:
            raise credentials_exception
        except Exception:
            raise credentials_exception

    def verify_access_token(self, token, credentials_exception) -> TokenData | HTTPException:
        """
        Verify the access token
        :author nhan.tran:
        :date 20-05-2024:
        :param token:
        :param credentials_exception:
        :return: TokenData | HTTPException
        """
        try:
            payload = jwt.decode(token, self._security.get_secret_key(), algorithms=[self._security.get_algorithm()])
            logging.info("payload", payload)
            user_id = payload.get("user_id")

            if user_id is None:
                raise credentials_exception

            token_data = TokenData(id=str(user_id))
            return token_data
        except jwt.ExpiredSignatureError:
            raise credentials_exception
        except jwt.JWTError:
            raise credentials_exception
        except Exception:
            raise credentials_exception

    def refresh_access_token(self, token) -> str | Exception:
        """
        Refresh the access token
        :author nhan.tran:
        :date 20-05-2024:
        :param token:
        :return: str | Exception
        """
        try:
            payload = jwt.decode(token,
                                 self._security.get_refresh_secret_key(),
                                 algorithms=[self._security.get_algorithm()])
            access_token = self.create_access_token(data={"user_id": payload["user_id"]})
            return access_token
        except Exception as e:
            raise e

    @staticmethod
    def verify_password(plain_password, hashed_password) -> bool:
        """
        Verify the password
        :author nhan.tran:
        :date 20-05-2024:
        :param plain_password:
        :param hashed_password:
        :return: bool
        """
        return verify(plain_password, hashed_password)
