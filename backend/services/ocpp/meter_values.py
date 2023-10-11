from ocpp.v16.call_result import MeterValuesPayload
from ocpp.v16.enums import Action
from pyocpp_contrib.decorators import response_call_result


@response_call_result(Action.MeterValues)
async def process_meter_values(session, event) -> MeterValuesPayload:
    return MeterValuesPayload()
