from ocpp.v16.call_result import SecurityEventNotificationPayload

from ocpp.v16.enums import Action
from pyocpp_contrib.decorators import response_call_result


@response_call_result(Action.SecurityEventNotification)
async def process_security_event_notification(session, event) -> SecurityEventNotificationPayload:
    return SecurityEventNotificationPayload()
