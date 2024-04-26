import logging

from fastapi.responses import JSONResponse
from fastapi import status, HTTPException
from pydantic.main import BaseModel


class ServiceWrapper:
    @staticmethod
    def async_wrapper(func):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                if isinstance(result, HTTPException):
                    raise result

                if isinstance(result, (JSONResponse, dict, list)):
                    return result

                if isinstance(result, str):
                    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": result})

                if isinstance(result, BaseModel):
                    return JSONResponse(status_code=status.HTTP_200_OK, content=result.dict(exclude_unset=True))

                return result.__dict__
            except HTTPException as e:
                logging.error("====================================")
                logging.error("HTTPException: " + e.detail)
                logging.error("====================================")
                try:
                    status_code, message = e.detail.split(": ")
                    status_code = int(status_code)
                except ValueError:
                    status_code, message = e.status_code, e.detail
                return JSONResponse(status_code=int(status_code), content={"message": message})
            except Exception as e:
                logging.error("====================================")
                logging.error("Exception: " + str(e))
                logging.error("====================================")
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})

        return wrapper

    @staticmethod
    def sync_wrapper(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException as e:
                logging.error("HTTPException: " + e.detail)
                try:
                    status_code, message = e.detail.split(": ")
                    status_code = int(status_code)
                except ValueError:
                    status_code, message = e.status_code, e.detail

                return JSONResponse(status_code=int(status_code), content={"message": message})
            except Exception as e:
                logging.error("====================================")
                logging.error("Exception: " + str(e))
                logging.error("====================================")
                return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"message": str(e)})
        return wrapper
