from typing import Callable

import arrow
from fastapi.routing import APIRoute
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from core.database import get_contextual_session
from core.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, UTC_DATETIME_FORMAT
from core.utils import now
from exceptions import NotAuthenticated
from models import Operator
from views.auth import AuthToken
from views.operators import CreateOperatorView

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
cookie_name = "token"


async def get_operator(session: AsyncSession, value) -> Operator:
    result = await session.execute(select(Operator).where(or_(Operator.email == value, Operator.id == value)))
    return result.scalars().first()


async def create_operator(session: AsyncSession, data: CreateOperatorView) -> Operator:
    data.password = pwd_context.hash(data.password)
    operator = Operator(**data.dict())
    session.add(operator)
    return operator


async def extract_token(request: Request) -> AuthToken | str:
    token = request.cookies.get(cookie_name)

    try:
        token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return AuthToken(**token)
    except Exception:
        return ""


async def create_token(operator: str) -> str:
    token = AuthToken(
        operator=str(operator),
        expired=now().shift(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) \
            .datetime.strftime(UTC_DATETIME_FORMAT)
    )

    return jwt.encode(token.dict(), SECRET_KEY, algorithm=ALGORITHM)


async def refresh_token(request: Request, response: Response):
    old_token = await extract_token(request)
    if not old_token:
        return
    new_token = await create_token(old_token.operator)
    response.set_cookie(cookie_name, new_token)


class AuthRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            token = await extract_token(request)
            if not token:
                raise NotAuthenticated

            async with get_contextual_session() as session:
                operator = await get_operator(session, token.operator)
                if arrow.get(token.expired) < now() or not operator:
                    raise NotAuthenticated
                request.state.operator = operator
            response: Response = await original_route_handler(request)
            return response

        return custom_route_handler
