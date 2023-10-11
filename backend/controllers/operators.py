import http

from fastapi import Response, Request
from loguru import logger

from core.database import get_contextual_session
from exceptions import NotAuthenticated
from routers import AnonymousRouter, AuthenticatedRouter
from services.operators import pwd_context, get_operator, create_token, cookie_name
from views.operators import LoginView, ReadOperatorView

operators_public_router = AnonymousRouter()
operators_private_router = AuthenticatedRouter()


@operators_private_router.get(
    "/me",
    status_code=http.HTTPStatus.OK,
    response_model=ReadOperatorView
)
async def retrieve_operator(request: Request):
    return request.state.operator


@operators_public_router.post(
    "/login",
    status_code=http.HTTPStatus.ACCEPTED,
    response_model=ReadOperatorView
)
async def login(response: Response, data: LoginView):
    logger.info(f"Start login (user={data.email})")
    error_message = "Invalid login or password"
    async with get_contextual_session() as session:
        operator = await get_operator(session, data.email)
        if not operator:
            raise NotAuthenticated(detail=error_message)

        if not pwd_context.verify(data.password, operator.password):
            raise NotAuthenticated(detail=error_message)

    token = await create_token(operator.id)
    response.set_cookie(cookie_name, token)
    return operator


@operators_private_router.post("/logout")
async def logout():
    logger.info(f"Start logout.")
    raise NotAuthenticated
