from typing import List

from fastapi import status

from core.cache import ActionCache
from routers import AuthenticatedRouter
from views.actions import ActionView

actions_router = AuthenticatedRouter(
    prefix="/actions",
    tags=["actions"]
)


@actions_router.get(
    "/{garage_id}",
    status_code=status.HTTP_200_OK,
    response_model=List[ActionView]
)
async def list_actions(garage_id):
    cache = ActionCache()
    return await cache.get_all_actions(garage_id)
