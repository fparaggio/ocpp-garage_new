from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import List

from ocpp.v16.call import StatusNotificationPayload
from ocpp.v16.enums import ChargePointStatus
from pyocpp_contrib.v16.views.events import StatusNotificationCallEvent
from sqlalchemy import select, update, func, or_, String, delete
from sqlalchemy.sql import selectable

import models as models
from models import ChargePoint
from views.charge_points import CreateChargPointView, UpdateChargPointView


async def update_connectors(session, event: StatusNotificationCallEvent):
    charge_point = await get_charge_point(session, event.charge_point_id)
    connectors = deepcopy(charge_point.connectors)
    if not event.payload.connector_id:
        charge_point.status = event.payload.status
    else:
        for idx, data in enumerate(connectors):
            connector = StatusNotificationPayload(**data)
            if connector.connector_id == event.payload.connector_id:
                connectors[idx].update(asdict(event.payload))
                break
        else:
            connectors.append(asdict(event.payload))

    charge_point.connectors = connectors
    session.add(charge_point)


async def reset_connectors(session, charge_point_id: str):
    charge_point = await get_charge_point(session, charge_point_id)
    charge_point.connectors.clear()


async def reset_charge_points(session):
    charge_points = await list_simple_charge_points(session, all=True)
    for charge_point in charge_points:
        await update_charge_point(session, charge_point.id, UpdateChargPointView(status=ChargePointStatus.unavailable))
        await reset_connectors(session, charge_point.id)


async def build_charge_points_query(search: str) -> selectable:
    criterias = [
        ChargePoint.is_active.is_(True)
    ]
    query = select(ChargePoint).outerjoin(models.Driver)
    for criteria in criterias:
        query = query.where(criteria)
    query = query.order_by(ChargePoint.updated_at.asc())
    if search:
        query = query.where(or_(
            func.lower(ChargePoint.id).contains(func.lower(search)),
            func.cast(ChargePoint.status, String).ilike(f"{search}%"),
            func.lower(ChargePoint.location).contains(func.lower(search)),
            func.lower(models.Driver.first_name).contains(func.lower(search)),
            func.lower(models.Driver.last_name).contains(func.lower(search))
        ))
    return query


async def get_charge_point(session, charge_point_id) -> ChargePoint | None:
    result = await session.execute(select(ChargePoint).where(ChargePoint.id == charge_point_id))
    return result.scalars().first()


async def create_charge_point(session, data: CreateChargPointView):
    charge_point = ChargePoint(**data.dict())
    session.add(charge_point)
    return charge_point


async def update_charge_point(
        session,
        charge_point_id: str,
        data
) -> None:
    await session.execute(update(ChargePoint) \
                          .where(ChargePoint.id == charge_point_id) \
                          .values(**data.dict(exclude_unset=True)))


async def remove_charge_point(session, charge_point_id: str) -> None:
    query = delete(ChargePoint) \
        .where(ChargePoint.id == charge_point_id)
    await session.execute(query)


async def list_simple_charge_points(session, all=False) -> List[ChargePoint]:
    query = select(ChargePoint)
    if not all:
        query = query.where(ChargePoint.driver_id.is_(None))
    query = query.with_only_columns(ChargePoint.id, ChargePoint.location, ChargePoint.status, ChargePoint.connectors)
    result = await session.execute(query)
    return result.fetchall()
