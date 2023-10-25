from loguru import logger
from ocpp.v16.call import RemoteStopTransactionPayload
from ocpp.v16.enums import Action, RemoteStartStopStatus
from pyocpp_contrib.decorators import send_call, contextable, use_context

from core.cache import ActionCache
from core.fields import TransactionStatus
from models import Transaction
from services.charge_points import get_charge_point
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
    charge_point = await get_charge_point(session, charge_point_id)

    logger.info(
        f"RemoteStopTransaction -> | prepared payload={payload} (charge_point_id={charge_point_id}, transaction={transaction})")

    cache = ActionCache()
    action = ActionView(
        message_id=message_id,
        charge_point_id=charge_point_id,
        body=f"Stop transaction"
    )
    await cache.insert(charge_point.garage_id, action)

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
    charge_point = await get_charge_point(session, event.charge_point_id)

    if RemoteStartStopStatus(event.payload.status) is RemoteStartStopStatus.accepted:
        await cache.update_status(charge_point.garage_id, event.message_id, status=TransactionStatus.completed)
    else:
        await cache.update_status(charge_point.garage_id, event.message_id, status=TransactionStatus.faulted)
