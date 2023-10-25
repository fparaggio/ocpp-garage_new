from loguru import logger
from ocpp.v16.call import ResetPayload
from ocpp.v16.enums import ResetType, Action, ResetStatus, ChargePointStatus
from pyocpp_contrib.decorators import send_call, contextable, use_context

from core.cache import ActionCache
from core.fields import TransactionStatus
from services.charge_points import get_charge_point
from views.actions import ActionView


@contextable
@send_call(Action.Reset)
async def process_reset(
        session,
        charge_point_id: str,
        message_id: str
) -> ResetPayload:
    payload = ResetPayload(type=ResetType.soft)
    logger.info(f"Reset -> | prepared payload={payload}")

    charge_point = await get_charge_point(session, charge_point_id)

    cache = ActionCache()
    action = ActionView(
        message_id=message_id,
        charge_point_id=charge_point_id,
        body="Reset station"
    )
    await cache.insert(charge_point.garage_id, action)

    return payload


@use_context
async def process_reset_call_result(
        session,
        event,
        context: ResetPayload | None = None
):
    logger.info(f"<- Reset | start process call result response (event={event}, context={context})")
    cache = ActionCache()

    charge_point = await get_charge_point(session, event.charge_point_id)

    if ResetStatus(event.payload.status) is ResetStatus.accepted:
        await cache.update_status(charge_point.garage_id, event.message_id, status=TransactionStatus.completed)
        charge_point.connectors.clear()
        charge_point.status = ChargePointStatus.unavailable
        logger.info(f"<- Reset | refused reset by station (event={event}, context={context})")

    if ResetStatus(event.payload.status) is ResetStatus.rejected:
        await cache.update_status(charge_point.garage_id, event.message_id, status=TransactionStatus.faulted)
