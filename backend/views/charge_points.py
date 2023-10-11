from __future__ import annotations

from datetime import datetime
from typing import List, Dict

from ocpp.v16.call import StatusNotificationPayload
from ocpp.v16.enums import ChargePointStatus
from pydantic import BaseModel

from views import PaginationView


class ChargePointUpdateStatusView(BaseModel):
    status: ChargePointStatus
    connectors: Dict | None = None


class CreateChargPointView(BaseModel):
    id: str
    description: str | None = None
    vendor: str | None = None
    serial_number: str | None = None
    model: str | None = None
    location: str | None = None


class UpdateChargPointView(BaseModel):
    driver_id: str | None = None
    description: str | None = None
    location: str | None = None
    status: ChargePointStatus | None = None


class ChargePointView(BaseModel):
    id: str
    description: str | None = None
    status: ChargePointStatus
    model: str | None = None
    vendor: str | None = None
    location: str | None = None
    updated_at: datetime | None = None
    connectors: List[StatusNotificationPayload]

    class Config:
        orm_mode = True


class SimpleChargePoint(BaseModel):
    id: str
    status: ChargePointStatus
    location: str | None = None
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class PaginatedChargePointsView(BaseModel):
    items: List[SimpleChargePoint]
    pagination: PaginationView
