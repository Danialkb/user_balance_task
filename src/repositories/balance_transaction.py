from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserBalanceTransaction


class IUserBalanceTransactionRepository(ABC):
    @abstractmethod
    async def create(
        self,
        user_id: UUID,
        amount: int,
        amount_before: int,
        amount_after: int,
        transaction_type: str,
        balance_id: UUID,
    ) -> UserBalanceTransaction:
        ...


class UserBalanceTransactionRepository(IUserBalanceTransactionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: UUID,
        amount: int,
        amount_before: int,
        amount_after: int,
        transaction_type: str,
        balance_id: UUID,
    ) -> UserBalanceTransaction:
        transaction = UserBalanceTransaction(
            user_id=user_id,
            amount=amount,
            amount_before=amount_before,
            amount_after=amount_after,
            transaction_type=transaction_type,
            balance_id=balance_id,
        )
        self.session.add(transaction)
        return transaction
