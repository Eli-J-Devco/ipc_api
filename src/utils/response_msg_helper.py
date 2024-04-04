from fastapi.responses import JSONResponse


def formatMessage(message: str, status: int) -> dict:
    return JSONResponse(content={"message": message}, status_code=status)
