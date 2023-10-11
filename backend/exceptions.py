import re
from http import HTTPStatus
from traceback import format_exc

from fastapi import HTTPException
from loguru import logger
from sqlalchemy.exc import IntegrityError
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from app import app
from core.settings import DEBUG
from views import ErrorContent


class NotAuthenticated(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            status_code=HTTPStatus.UNAUTHORIZED,
            *args,
            **kwargs
        )


class Forbidden(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            status_code=HTTPStatus.FORBIDDEN,
            *args,
            **kwargs
        )


class BadRequest(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=HTTPStatus.BAD_REQUEST,
                         *args,
                         **kwargs)


class NotFound(HTTPException):
    def __init__(self, *args, **kwargs):
        super().__init__(status_code=HTTPStatus.NOT_FOUND,
                         *args,
                         **kwargs)


@app.exception_handler(IntegrityError)
async def unique_violation_exception_handler(request: Request, exc: IntegrityError):
    pattern = re.compile(r"Key \((.*?)\)=\((.*?)\) (.*)")
    name, value, reason = pattern.search(exc.args[0]).groups()
    context = ErrorContent(detail=f"'{value}' {reason}", key=name)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=context.dict(),
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc):
    _exc = format_exc()
    context = {
        "path": request.url,
        "params": request.query_params,
        "body": request.json(),
        "method": request.method,
        "state": request.state
    }
    logger.error("Caught unrecognized server error (request: %r, error: %r" % (context, _exc))
    if DEBUG:
        content = _exc
    else:
        content = "Something went wrong."
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=content,
    )
