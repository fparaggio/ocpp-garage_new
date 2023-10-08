from loguru import logger
from ocpp.v16.call import RemoteStartTransactionPayload
from ocpp.v16.enums import ChargePointStatus, Action

from pyocpp_contrib.decorators import send_call, contextable, use_context
from services.charge_points import get_charge_point


@contextable
@send_call(Action.RemoteStartTransaction)
async def process_remote_start_transaction_call(
        session,
        charge_point_id: str,
        connector_id: int,
        id_tag: str
) -> RemoteStartTransactionPayload:
    charge_point = await get_charge_point(session, charge_point_id)
    logger.info(
        f"RemoteStartTransaction -> | Found charge point (charge_point_id={charge_point_id}, connector_id={connector_id}, id_tag={id_tag})")
    data = dict(status=ChargePointStatus.preparing)
    await charge_point.update_connector(session, connector_id, data)
    logger.info(
        f"RemoteStartTransaction -> | Updated connector with data={data} (charge_point_id={charge_point_id}, connector_id={connector_id}, id_tag={id_tag})")
    payload = RemoteStartTransactionPayload(
        connector_id=connector_id,
        id_tag=id_tag
    )
    logger.info(
        f"RemoteStartTransaction -> | Prepared payload={payload} (charge_point_id={charge_point_id}, connector_id={connector_id}, id_tag={id_tag})")
    return payload


@use_context
async def process_remote_start_transaction_call_result(
        session,
        event,
        context: RemoteStartTransactionPayload | None = None
):
    logger.info(f"<- RemoteStartTransaction | Start process call result response (event={event}, context={context}.)")
