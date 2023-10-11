from copy import deepcopy

from loguru import logger
from ocpp.v16.enums import Action, ChargePointStatus

from core.database import get_contextual_session
from pyocpp_contrib.decorators import prepare_event, message_id_generator
from pyocpp_contrib.enums import ConnectionAction
from services.charge_points import update_charge_point, reset_connectors
from services.ocpp.authorize import process_authorize
from services.ocpp.boot_notification import process_boot_notification
from services.ocpp.change_availability import process_change_availability_call_result
from services.ocpp.change_configuration import process_change_configration_call, configuration
from services.ocpp.heartbeat import process_heartbeat
from services.ocpp.meter_values import process_meter_values
from services.ocpp.remote_start_transaction import process_remote_start_transaction_call_result
from services.ocpp.remote_stop_transaction import process_remote_stop_transaction_call_result
from services.ocpp.reset import process_reset_call_result
from services.ocpp.security_event_notification import process_security_event_notification
from services.ocpp.start_transaction import process_start_transaction
from services.ocpp.status_notification import process_status_notification
from services.ocpp.stop_transaction import process_stop_transaction
from services.ocpp.unlock_connector import process_unlock_connector_call_result
from views.charge_points import ChargePointUpdateStatusView


@prepare_event
async def process_event(event):
    if isinstance(event, dict):
        logger.error(f"Could not recognize event from the station (event={event}.)")
        return
    else:
        logger.info(f"Got event from charge point node (event={event})")

    async with get_contextual_session() as session:

        # Call messages
        if event.action is Action.MeterValues:
            await process_meter_values(session, deepcopy(event))
        if event.action is Action.StopTransaction:
            await process_stop_transaction(session, deepcopy(event))
        if event.action is Action.StartTransaction:
            await process_start_transaction(session, deepcopy(event))
        if event.action is Action.Authorize:
            await process_authorize(session, deepcopy(event))
        if event.action is Action.SecurityEventNotification:
            await process_security_event_notification(session, deepcopy(event))
        if event.action is Action.BootNotification:
            await process_boot_notification(session, deepcopy(event))
            for config in configuration:
                await process_change_configration_call(
                    config,
                    charge_point_id=event.charge_point_id,
                    message_id=message_id_generator()
                )
        if event.action is Action.StatusNotification:
            await process_status_notification(session, deepcopy(event))
        if event.action is Action.Heartbeat:
            await process_heartbeat(session, deepcopy(event))
        if event.action is ConnectionAction.lost_connection:
            data = ChargePointUpdateStatusView(status=ChargePointStatus.unavailable)
            await update_charge_point(session, charge_point_id=event.charge_point_id, data=data)
            await reset_connectors(session, event.charge_point_id)

        # Call result messages
        if event.action is Action.RemoteStartTransaction:
            await process_remote_start_transaction_call_result(session, deepcopy(event))
        if event.action is Action.RemoteStopTransaction:
            await process_remote_stop_transaction_call_result(session, deepcopy(event))
        if event.action is Action.ChangeAvailability:
            await process_change_availability_call_result(session, deepcopy(event))
        if event.action is Action.Reset:
            await process_reset_call_result(session, deepcopy(event))
        if event.action is Action.UnlockConnector:
            await process_unlock_connector_call_result(session, deepcopy(event))

        await session.commit()
        logger.info(f"Successfully completed process event={event}")

        return event
