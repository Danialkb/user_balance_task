import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.models import UserBalance


class TestUserBalanceEndpoints:
    async def test_get_user_balance_not_found(self, async_client):
        user_id = uuid.uuid4()
        response = await async_client.get(
            "/api/v1/user_balance", headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {"detail": "Balance not found"}

    async def test_get_user_balance_invalid_use_id(self, async_client):
        user_id = "invalid"
        response = await async_client.get(
            "/api/v1/user_balance", headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_get_user_balance_success(
        self, async_client, db_session: AsyncSession
    ):
        user_id = uuid.uuid4()
        balance = UserBalance(user_id=user_id, balance=100)
        db_session.add(balance)
        await db_session.commit()

        response = await async_client.get(
            "/api/v1/user_balance", headers={"X-User-Id": str(user_id)}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == str(user_id)
        assert data["balance"] == 100
