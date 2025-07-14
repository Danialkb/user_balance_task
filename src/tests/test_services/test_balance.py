import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import UserBalance
from repositories.user_balance import UserBalanceRepository


class TestUserBalanceRepository:
    def test_create(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        repo = UserBalanceRepository(db_session)

        result = repo.create(user_id)

        assert isinstance(result, UserBalance)
        assert result.user_id == user_id
        assert result.balance == 0

    async def test_get_existing(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        existing_balance = UserBalance(user_id=user_id, balance=200)
        db_session.add(existing_balance)
        await db_session.commit()

        repo = UserBalanceRepository(db_session)

        result = await repo.get(user_id)

        assert isinstance(result, UserBalance)
        assert result.user_id == user_id
        assert result.balance == 200

    async def test_get_not_found(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        repo = UserBalanceRepository(db_session)

        result = await repo.get(user_id)

        assert result is None

    async def test_add_balance(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        existing_balance = UserBalance(user_id=user_id, balance=300)
        db_session.add(existing_balance)
        await db_session.commit()

        repo = UserBalanceRepository(db_session)

        result = await repo.add_balance(user_id, 150)

        assert isinstance(result, UserBalance)
        assert result.balance == 450

    async def test_add_balance_not_found(self, db_session: AsyncSession):
        user_id = uuid.uuid4()
        repo = UserBalanceRepository(db_session)

        result = await repo.add_balance(user_id, 150)

        assert result is None

    @pytest.mark.parametrize("amount", [0, -100])
    async def test_add_balance_invalid_amount(
        self, db_session: AsyncSession, amount: int
    ):
        user_id = uuid.uuid4()
        repo = UserBalanceRepository(db_session)

        with pytest.raises(ValueError, match="Amount must be positive"):
            await repo.add_balance(user_id, amount)
