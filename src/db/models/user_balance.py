import uuid
from datetime import datetime

from sqlalchemy import func, DateTime, CheckConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.models.base import Base


class UserBalance(Base):
    __tablename__ = "user_balances"
    __table_args__ = (
        CheckConstraint("balance >= 0", name="non_negative_balance"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(index=True)
    balance: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
