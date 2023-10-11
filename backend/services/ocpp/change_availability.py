from loguru import logger
from ocpp.v16.call import ChangeAvailabilityPayload
from ocpp.v16.enums import AvailabilityType, Action

from pyocpp_contrib.decorators import send_call, contextable, use_context


@contextable
@send_call(Action.ChangeAvailability)
async def process_change_availability(
        charge_point_id: str,
        connector_id: int,
        type: AvailabilityType,
        message_id: str
) -> ChangeAvailabilityPayload:
    payload = ChangeAvailabilityPayload(connector_id=connector_id, type=type)
    logger.info(f"ChangeAvailability -> | prepared payload (charge_point_id={charge_point_id} payload={payload})")
    return payload


@use_context
async def process_change_availability_call_result(
        session,
        event,
        context: ChangeAvailabilityPayload | None = None
):
    logger.info(f"<- ChangeAvailability | start process call result response (event={event}, context={context})")
