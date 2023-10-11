from dataclasses import asdict

from ocpp.v16.call_result import AuthorizePayload
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import Action
from ocpp.v16.enums import AuthorizationStatus
from pyocpp_contrib.decorators import response_call_result

from services.charge_points import get_charge_point
from services.drivers import is_driver_authorized


@response_call_result(Action.Authorize)
async def process_authorize(session, event) -> AuthorizePayload:
    status = AuthorizationStatus.accepted
    charge_point = await get_charge_point(session, event.charge_point_id)
    if not charge_point.driver or not await is_driver_authorized(charge_point.driver):
        status = AuthorizationStatus.blocked

    return AuthorizePayload(id_tag_info=asdict(IdTagInfo(status=status)))
