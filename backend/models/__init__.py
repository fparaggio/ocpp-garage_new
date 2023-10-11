from __future__ import annotations

from copy import deepcopy
from typing import Dict

from ocpp.v16.call import StatusNotificationPayload
from ocpp.v16.enums import ChargePointStatus
from sqlalchemy import Column, String, ForeignKey, Enum, ARRAY, JSON, Integer, Sequence
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from core.database import Model
from core.fields import TransactionStatus


class Person(Model):
    __abstract__ = True

    email = Column(String(48), nullable=False, unique=True)
    first_name = Column(String(24), nullable=False, unique=False)
    last_name = Column(String(24), nullable=False, unique=False)
    address = Column(String(48), nullable=False, unique=False)

    def __repr__(self) -> str:
        return f"Driver: {self.id}, {self.email}"


class Operator(Person):
    __tablename__ = "operators"

    password = Column(String(124), nullable=False, unique=False)


class Driver(Person):
    __tablename__ = "drivers"

    billing_requisites = Column(JSON, default=dict())
    charge_points = relationship("ChargePoint",
                                 back_populates="driver",
                                 lazy="joined")


class ChargePoint(Model):
    __tablename__ = "charge_points"

    description = Column(String(124), nullable=True)
    status = Column(Enum(ChargePointStatus), default=ChargePointStatus.unavailable, index=True)
    vendor = Column(String, nullable=True)
    serial_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    model = Column(String, nullable=True)
    connectors = Column(MutableList.as_mutable(ARRAY(JSON)), default=list())

    driver_id = Column(String, ForeignKey("drivers.id"), nullable=True)
    driver = relationship("Driver", back_populates="charge_points", lazy="joined")

    async def update_connector(self, session, connector_id: int, payload: Dict) -> bool:
        connectors = deepcopy(self.connectors)
        for idx, data in enumerate(connectors):
            connector = StatusNotificationPayload(**data)
            if connector.connector_id == connector_id:
                connectors[idx].update(payload)
                self.connectors = connectors
                session.add(self)
                return True
        return False

    def __repr__(self):
        return f"ChargePoint (id={self.id}, status={self.status}, location={self.location})"


class Transaction(Model):
    __tablename__ = "transactions"
    transaction_id_seq = Sequence("transaction_id_seq")

    driver = Column(String, nullable=False)
    meter_start = Column(Integer, nullable=False)
    meter_stop = Column(Integer, nullable=True)
    charge_point = Column(String, nullable=False)
    connector = Column(Integer, nullable=False)
    transaction_id = Column(Integer, transaction_id_seq, server_default=transaction_id_seq.next_value())
    status = Column(Enum(TransactionStatus), default=TransactionStatus.in_progress)

    def __repr__(self):
        return f"Transaction (id={self.id}, charge_point={self.charge_point}, transaction_id={self.transaction_id}, status={self.status})"
