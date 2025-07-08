from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class UserBalanceResponse(BaseModel):
    id: UUID
    user_id: UUID
    balance: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserBalanceAddSchema(BaseModel):
    amount: int

    @field_validator("amount")
    def validate_amount(cls, amount: int):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        return amount
