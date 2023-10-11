from ocpp.v16.call_result import BootNotificationPayload
from ocpp.v16.enums import RegistrationStatus, Action

from core.utils import get_utc_as_string
from pyocpp_contrib.decorators import response_call_result
from services.charge_points import get_charge_point


@response_call_result(Action.BootNotification)
async def process_boot_notification(session, event) -> BootNotificationPayload:
    charge_point = await get_charge_point(session, event.charge_point_id)
    charge_point.model = event.payload.charge_point_model
    charge_point.vendor = event.payload.charge_point_vendor
    charge_point.serial_number = event.payload.charge_point_serial_number
    session.add(charge_point)

    return BootNotificationPayload(
        current_time=get_utc_as_string(),
        interval=60,
        status=RegistrationStatus.accepted
    )
