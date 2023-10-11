from http import HTTPStatus

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from core.settings import ALLOWED_ORIGIN

app = FastAPI()

origins = [ALLOWED_ORIGIN]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("authentication")
async def refresh_auth_token(request: Request, call_next):
    from services.operators import cookie_name, refresh_token

    response: Response = await call_next(request)
    if HTTPStatus(response.status_code) is HTTPStatus.UNAUTHORIZED:
        response.delete_cookie(cookie_name)
    else:
        # Don't refresh cookies for periodic requests from the frontend
        if request.query_params.get("periodic"):
            pass
        else:
            await refresh_token(request, response)
    return response
