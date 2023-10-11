from ocpp.v16.call_result import StatusNotificationPayload
from ocpp.v16.enums import Action
from pyocpp_contrib.decorators import response_call_result

from services.charge_points import update_connectors


@response_call_result(Action.StatusNotification)
async def process_status_notification(
        session,
        event
) -> StatusNotificationPayload:
    await update_connectors(session, event)
    return StatusNotificationPayload()
