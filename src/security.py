from functools import reduce

from fastapi.security import HTTPBasic

from .config import env_config


class Security:
    def __init__(self,
                 secret_key=None,
                 refresh_secret_key=None,
                 algorithm=None,
                 access_token_expire_value=60,
                 access_token_expire_unit="m",
                 refresh_token_expire_unit="m",
                 refresh_token_expire_value=60 * 24 * 7):
        self._secret_key = secret_key
        self._refresh_secret_key = refresh_secret_key
        self.algorithm = algorithm
        self.access_token_expire_value = access_token_expire_value
        self.access_token_expire_unit = access_token_expire_unit
        self.refresh_token_expire_value = refresh_token_expire_value
        self.refresh_token_expire_unit = refresh_token_expire_unit
        self.security = HTTPBasic()

    def set_secret_key(self, secret_key):
        self._secret_key = secret_key

    def set_refresh_secret_key(self, refresh_secret_key):
        self._refresh_secret_key = refresh_secret_key

    def set_algorithm(self, algorithm):
        self.algorithm = algorithm

    def set_access_token_timeout(self, access_token_expire_value, access_token_expire_unit):
        self.access_token_expire_value = access_token_expire_value
        self.access_token_expire_unit = access_token_expire_unit

    def set_refresh_token_timeout(self, refresh_token_expire_value, refresh_token_expire_unit):
        self.refresh_token_expire_value = refresh_token_expire_value
        self.refresh_token_expire_unit = refresh_token_expire_unit

    def get_secret_key(self):
        return self._secret_key

    def get_refresh_secret_key(self):
        return self._refresh_secret_key

    def get_algorithm(self):
        return self.algorithm

    def get_access_token_timeout(self):
        return self.access_token_expire_value, self.access_token_expire_unit

    def get_refresh_token_timeout(self):
        return self.refresh_token_expire_value, self.refresh_token_expire_unit

    def get_security(self):
        return self.security


class SecurityRepository:
    __security = None

    @staticmethod
    def get_security_config():
        if SecurityRepository.__security is None:
            SecurityRepository.__security = Security(
                secret_key=env_config.SECRET_KEY,
                refresh_secret_key=env_config.REFRESH_SECRET_KEY,
                algorithm=env_config.ALGORITHM,
                access_token_expire_value=int(env_config.ACCESS_TOKEN_EXPIRE_VALUE),
                access_token_expire_unit=env_config.ACCESS_TOKEN_EXPIRE_UNIT,
                refresh_token_expire_value=int(
                    reduce(lambda x, y: x * y,
                           map(lambda x: int(x),
                               env_config.REFRESH_TOKEN_EXPIRE_VALUE.split("*")))),
                refresh_token_expire_unit=env_config.REFRESH_TOKEN_EXPIRE_UNIT,
            )
        return SecurityRepository.__security
