import uuid
from datetime import datetime

from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class UserBalanceTransaction(Base):
    __tablename__ = "user_balance_transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    amount: Mapped[int]
    amount_before: Mapped[int]
    amount_after: Mapped[int]

    # metadata
    transaction_type: Mapped[str]  # Quiz reward, Purchase etc ...
    balance_id: Mapped[uuid.UUID] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
