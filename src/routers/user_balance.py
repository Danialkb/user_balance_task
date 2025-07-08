from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from dependencies.user import get_user_id
from schemas.user_balance import UserBalanceResponse, UserBalanceAddSchema
from services.uow import UnitOfWork
from services.user_balance import UserBalanceService

router = APIRouter(prefix="/api/v1/user_balance", tags=["User Balance V1"])


@router.get("")
async def get_user_balance(
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserBalanceResponse:
    uow = UnitOfWork(session)
    balance_service = UserBalanceService(uow)

    balance = await balance_service.get_user_balance(user_id=user_id)
    if not balance:
        raise HTTPException(status_code=404, detail="Balance not found")
    return balance


@router.post("/add")
async def add_user_balance(
    data: UserBalanceAddSchema,
    user_id: UUID = Depends(get_user_id),
    session: AsyncSession = Depends(get_session),
) -> UserBalanceResponse:
    uow = UnitOfWork(session)
    balance_service = UserBalanceService(uow)
    return await balance_service.add_to_balance(user_id, data.amount)
