from loguru import logger
from ocpp.v16.call import RemoteStopTransactionPayload
from ocpp.v16.enums import Action, RemoteStartStopStatus

from core.cache import ActionCache
from core.fields import TransactionStatus
from models import Transaction
from pyocpp_contrib.decorators import send_call, contextable, use_context
from views.actions import ActionView


@contextable
@send_call(Action.RemoteStopTransaction)
async def process_remote_stop_transaction_call(
        session,
        charge_point_id: str,
        transaction: Transaction,
        message_id: str
) -> RemoteStopTransactionPayload:
    transaction.status = TransactionStatus.pending
    logger.info(
        f"RemoteStopTransaction -> | updated transactions status={transaction.status} (charge_point_id={charge_point_id}, transaction={transaction})")
    payload = RemoteStopTransactionPayload(transaction_id=transaction.transaction_id)
    logger.info(
        f"RemoteStopTransaction -> | prepared payload={payload} (charge_point_id={charge_point_id}, transaction={transaction})")

    cache = ActionCache()
    action = ActionView(
        message_id=message_id,
        charge_point_id=charge_point_id,
        body=f"Stop transaction"
    )
    await cache.insert(action)

    return payload


@use_context
async def process_remote_stop_transaction_call_result(
        session,
        event,
        context: RemoteStopTransactionPayload | None
):
    logger.info(
        f"<- RemoteStopTransaction | start process response from the station (event={event}, context={context}.)")
    cache = ActionCache()
    if RemoteStartStopStatus(event.payload.status) is RemoteStartStopStatus.accepted:
        await cache.update_status(event.message_id, status=TransactionStatus.completed)
    else:
        await cache.update_status(event.message_id, status=TransactionStatus.faulted)
