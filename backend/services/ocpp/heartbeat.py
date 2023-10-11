from ocpp.v16.call_result import HeartbeatPayload
from ocpp.v16.enums import Action
from ocpp.v16.enums import ChargePointStatus
from pyocpp_contrib.decorators import response_call_result

from core.utils import get_utc_as_string
from services.charge_points import update_charge_point
from views.charge_points import ChargePointUpdateStatusView


@response_call_result(Action.Heartbeat)
async def process_heartbeat(session, event) -> HeartbeatPayload:
    data = ChargePointUpdateStatusView(status=ChargePointStatus.available)
    await update_charge_point(session, event.charge_point_id, data=data)

    return HeartbeatPayload(current_time=get_utc_as_string())
