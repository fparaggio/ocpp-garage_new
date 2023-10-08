from ocpp.v16.call import UnlockConnectorPayload
from ocpp.v16.enums import Action
from pyocpp_contrib.decorators import send_call, contextable, use_context


@contextable
@send_call(Action.UnlockConnector)
async def process_unlock_connector(
        charge_point_id: str,
        connector_id: int
) -> UnlockConnectorPayload:
    return UnlockConnectorPayload(
        connector_id=connector_id
    )


@use_context
async def process_unlock_connector_call_result(
        session,
        event,
        context: UnlockConnectorPayload | None = None
):
    pass
