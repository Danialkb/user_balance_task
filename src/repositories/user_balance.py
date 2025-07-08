from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserBalance


class IUserBalanceRepository(ABC):
    @abstractmethod
    async def create(self, user_id: UUID) -> UserBalance:
        ...

    @abstractmethod
    async def get(self, user_id: UUID) -> UserBalance | None:
        ...

    @abstractmethod
    async def add_balance(self, user_id: UUID, amount: int) -> UserBalance | None:
        ...


class UserBalanceRepository(IUserBalanceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: UUID) -> UserBalance:
        balance = UserBalance(user_id=user_id, balance=0)
        self.session.add(balance)
        return balance

    async def add_balance(self, user_id: UUID, amount: int) -> UserBalance | None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        stmt = (
            select(UserBalance).where(UserBalance.user_id == user_id).with_for_update()
        )
        result = await self.session.execute(stmt)
        balance = result.scalar_one_or_none()

        if not balance:
            return

        balance.balance += amount
        return balance

    async def refresh(self, balance: UserBalance):
        await self.session.refresh(balance)

    async def get(self, user_id: UUID) -> UserBalance | None:
        stmt = select(UserBalance).where(UserBalance.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
