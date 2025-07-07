from uuid import UUID

from repositories.user_balance import IUserBalanceRepository
from schemas.user_balance import UserBalanceResponse


class UserBalanceService:
    def __init__(self, balance_repo: IUserBalanceRepository):
        self.balance_repo = balance_repo

    async def add_to_balance(self, user_id: UUID, amount: int) -> UserBalanceResponse:
        if not await self.get_user_balance(user_id):
            await self.create(user_id)

        balance = await self.balance_repo.add_balance(user_id, amount)
        return UserBalanceResponse.model_validate(balance)

    async def create(self, user_id: UUID) -> UserBalanceResponse:
        balance = await self.balance_repo.create(user_id)
        return UserBalanceResponse.model_validate(balance)

    async def get_user_balance(self, user_id: UUID) -> UserBalanceResponse | None:
        balance = await self.balance_repo.get(user_id)
        if not balance:
            return None
        return UserBalanceResponse.model_validate(balance)
