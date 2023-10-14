from __future__ import annotations

from typing import List

from sqlalchemy import select, update, func, or_, String, delete
from sqlalchemy.sql import selectable

from models import Driver, ChargePoint
from services.charge_points import update_charge_point
from views.charge_points import UpdateChargPointView
from views.drivers import CreateDriverView, UpdateDriverView


async def is_driver_authorized(driver: Driver):
    return driver.is_active


async def build_drivers_query(search: str, extra_criterias: List | None = None) -> selectable:
    query = select(Driver)
    if extra_criterias:
        for criteria in extra_criterias:
            query = query.where(criteria)
    query = query.order_by(Driver.updated_at.asc())
    if search:
        query = query.where(or_(
            func.lower(Driver.email).contains(func.lower(search)),
            func.cast(Driver.address, String).ilike(f"{search}%"),
            func.lower(Driver.first_name).contains(func.lower(search)),
            func.lower(Driver.last_name).contains(func.lower(search)),
        ))
    return query


async def get_driver(session, garage_id, driver_id) -> Driver | None:
    result = await session.execute(
        select(Driver) \
            .where(Driver.id == driver_id) \
            .where(Driver.garage_id == garage_id)
    )
    return result.scalars().first()


async def create_driver(session, garage_id: str, data: CreateDriverView):
    driver = Driver(garage_id=garage_id, **data.dict())
    session.add(driver)
    return driver


async def update_driver(
        session,
        garage_id: str,
        driver_id: str,
        data: UpdateDriverView
) -> None:
    payload = data.dict(exclude_unset=True)
    charge_point_id = payload.pop("charge_point_id", None)
    if charge_point_id:
        data = UpdateChargPointView(driver_id=driver_id)
        await update_charge_point(session, charge_point_id, data)
    if payload:
        await session.execute(update(Driver) \
                              .where(Driver.id == driver_id) \
                              .hwere(Driver.garage_id == garage_id) \
                              .values(**payload))


async def remove_driver(session, garage_id: str, driver_id: str) -> None:
    await session.execute(update(ChargePoint) \
                          .where(ChargePoint.driver_id == driver_id) \
                          .values({"driver_id": None}))
    query = delete(Driver) \
        .where(Driver.id == driver_id) \
        .where(Driver.garage_id == garage_id)
    await session.execute(query)
