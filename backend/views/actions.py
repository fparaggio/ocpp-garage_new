from pydantic import BaseModel

from core.fields import TransactionStatus


class ActionView(BaseModel):
    message_id: str
    charge_point_id: str
    body: str
    status: TransactionStatus = TransactionStatus.pending
