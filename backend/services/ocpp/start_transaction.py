from dataclasses import asdict

from loguru import logger
from ocpp.v16.call_result import StartTransactionPayload
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import Action
from ocpp.v16.enums import AuthorizationStatus, ChargePointStatus

from pyocpp_contrib.decorators import response_call_result
from services.charge_points import get_charge_point
from services.drivers import is_driver_authorized
from services.transactions import create_transaction
from views.transactions import CreateTransactionView


@response_call_result(Action.StartTransaction)
async def process_start_transaction(session, event) -> StartTransactionPayload:
    logger.info(f"StartTransaction -> | start process call event (event={event})")
    charge_point = await get_charge_point(session, event.charge_point_id)

    # It is a good practice to always create transaction
    view = CreateTransactionView(
        driver=charge_point.driver.email,
        meter_start=event.payload.meter_start,
        charge_point=charge_point.id,
        connector=event.payload.connector_id
    )
    transaction = await create_transaction(session, view)
    await session.flush()
    logger.info(
        f"StartTransaction -> | created new transaction with data={view} (charge_point_id={charge_point.id}, transaction={transaction})")

    status = AuthorizationStatus.accepted
    if not await is_driver_authorized(charge_point.driver):
        logger.error(
            f"StartTransaction -> | refused charging due to inactive driver (charge_point_id={charge_point.id}, driver={charge_point.driver})")
        status = AuthorizationStatus.blocked

    if status is AuthorizationStatus.accepted:
        await charge_point.update_connector(
            session,
            event.payload.connector_id,
            dict(status=ChargePointStatus.charging)
        )
        logger.info(
            f"StartTransaction -> | allowed charging (charge_point_id={charge_point.id}, driver={charge_point.driver}, connectors={charge_point.connectors})")

    payload = StartTransactionPayload(
        transaction_id=transaction.transaction_id,
        id_tag_info=asdict(IdTagInfo(status=status))
    )
    logger.info(
        f"StartTransaction -> | prepared payload={payload}, charge_point_id={charge_point.id}, driver={charge_point.driver}")
    return payload
