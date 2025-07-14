from uuid import UUID

from pydantic import BaseModel

from enums import TransactionType


class BalanceUpdateMessage(BaseModel):
    user_id: UUID
    amount: int
    type: TransactionType
