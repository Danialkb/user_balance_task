from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.balance_transaction import (
    IUserBalanceTransactionRepository,
    UserBalanceTransactionRepository,
)
from repositories.user_balance import UserBalanceRepository, IUserBalanceRepository


class IUnitOfWork(ABC):
    user_balance_repo: IUserBalanceRepository
    balance_transaction_repo: IUserBalanceTransactionRepository

    @abstractmethod
    async def commit(self):
        ...

    @abstractmethod
    async def rollback(self):
        ...

    @abstractmethod
    async def close(self):
        ...


class UnitOfWork(IUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_balance_repo = UserBalanceRepository(session)
        self.balance_transaction_repo = UserBalanceTransactionRepository(session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.rollback()
                return
            await self.commit()
        finally:
            await self.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def close(self):
        await self.session.close()
