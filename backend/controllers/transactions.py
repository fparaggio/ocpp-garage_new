from typing import Tuple

from fastapi import Depends, Request
from starlette import status

from core.database import get_contextual_session
from routers import AuthenticatedRouter
from services.ocpp.remote_start_transaction import process_remote_start_transaction
from services.ocpp.remote_stop_transaction import process_remote_stop_transaction
from services.transactions import build_transactions_query, get_transaction
from utils import params_extractor, paginate
from views.transactions import PaginatedTransactionsView, InitTransactionView

transactions_router = AuthenticatedRouter(prefix="/transactions", tags=["transactions"])


@transactions_router.get(
    "/",
    status_code=status.HTTP_200_OK
)
async def list_transactions(
        search: str = "",
        params: Tuple = Depends(params_extractor)
) -> PaginatedTransactionsView:
    async with get_contextual_session() as session:
        items, pagination = await paginate(
            session,
            lambda: build_transactions_query(search),
            *params
        )
        return PaginatedTransactionsView(items=[item[0] for item in items], pagination=pagination)


@transactions_router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remote_start_transaction(
        data: InitTransactionView,
        request: Request
):
    async with get_contextual_session() as session:
        await process_remote_start_transaction(
            session,
            charge_point_id=data.charge_point_id,
            connector_id=data.connector_id,
            id_tag=request.state.operator.id
        )
        await session.commit()


@transactions_router.put(
    "/{transaction_uuid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def remote_stop_transaction(transaction_uuid: str):
    async with get_contextual_session() as session:
        transaction = await get_transaction(session, transaction_uuid)
        await process_remote_stop_transaction(
            session,
            transaction.charge_point,
            transaction
        )
        await session.commit()
