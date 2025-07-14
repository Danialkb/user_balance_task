import logging
from uuid import UUID

from enums import TransactionType
from schemas.user_balance import UserBalanceResponse
from services.uow import IUnitOfWork

logger = logging.getLogger(__name__)


class UserBalanceService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_to_balance(self, user_id: UUID, amount: int, transaction_type: TransactionType) -> UserBalanceResponse:
        logger.info(f"Adding balance bonus for User<{user_id}>")
        user_balance = await self.get_user_balance(user_id)
        if not user_balance:
            user_balance = await self.create(user_id)

        async with self.uow as uow_instance:
            balance_amount_before = user_balance.balance
            user_balance = await uow_instance.user_balance_repo.add_balance(
                user_id, amount
            )
            uow_instance.balance_transaction_repo.create(
                user_id=user_id,
                amount=amount,
                amount_before=balance_amount_before,
                amount_after=user_balance.balance,
                transaction_type=transaction_type.value,
                balance_id=user_balance.id,
            )
            await uow_instance.commit()
            await uow_instance.user_balance_repo.refresh(user_balance)
        return UserBalanceResponse.model_validate(user_balance)

    async def create(self, user_id: UUID) -> UserBalanceResponse:
        logger.info(f"Creating balance account User<{user_id}>")
        async with self.uow as uow_instance:
            balance = uow_instance.user_balance_repo.create(user_id)
        return UserBalanceResponse.model_validate(balance)

    async def get_user_balance(self, user_id: UUID) -> UserBalanceResponse | None:
        async with self.uow as uow_instance:
            balance = await uow_instance.user_balance_repo.get(user_id)
            if not balance:
                return None
        return UserBalanceResponse.model_validate(balance)
