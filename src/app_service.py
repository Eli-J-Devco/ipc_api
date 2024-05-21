# ********************************************************
# * Copyright 2023 NEXT WAVE ENERGY MONITORING INC.
# * All rights reserved.
# *
# *********************************************************/
from nest.core import Injectable
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBasicCredentials
from fastapi import FastAPI

from .config import env_config

import secrets

from .security import SecurityRepository


@Injectable
class AppService:
    def __init__(self):
        self.app_name = "IPC NEW VERSION"
        self.app_version = "1.0.0"
        self.description = "IPC API"

    @staticmethod
    def get_current_user(credentials: HTTPBasicCredentials = Depends(SecurityRepository
                                                                     .get_security_config().get_security())):
        correct_username = secrets.compare_digest(credentials.username, env_config.API_DOCS_USERNAME)
        correct_password = secrets.compare_digest(credentials.password, env_config.API_DOCS_PASSWORD)
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials.username

    def get_app_info(self):
        return {"app_name": self.app_name, "app_version": self.app_version}

    @staticmethod
    def get_app_docs():
        return get_swagger_ui_html(
            openapi_url="/openapi.json",
            title="docs",
            swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
            swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
        )

    @staticmethod
    def get_app_redoc():
        return get_redoc_html(
            openapi_url="/openapi.json",
            title="redocs",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
            redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
            with_google_fonts=True,
        )

    def get_openapi_json(self, app: FastAPI):
        return get_openapi(
            title=self.app_name,
            version=self.app_version,
            description=self.description,
            routes=app.routes,
        )
