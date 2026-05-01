# custom exceptions
# main used for logging in each exception
from fastapi import Request, status
from fastapi.responses import JSONResponse


class DetailedHTTPException(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    code = "SERVER_ERROR"

    def __init__(self, message: str):
        self.message = message


class NotFound(DetailedHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "NOT_FOUND"


class UnAuthorized(DetailedHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "UnAuthorized"


class BadRequest(DetailedHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "BAD_REQUEST"


class Conflict(DetailedHTTPException):
    status_code = status.HTTP_409_CONFLICT
    code = "CONFLICT"


async def exception_handler(
    request: Request,
    exc: DetailedHTTPException | NotFound | BadRequest | Conflict | UnAuthorized,
):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"error_code": exc.code, "message": exc.message},
    )
