import asyncio
import json
import logging
import logging.config

import pydantic
from aio_pika.abc import AbstractIncomingMessage

from db.session import async_session
from messaging.broker import MessageBroker
from messaging.consumer.messages import BalanceUpdateMessage
from services.uow import UnitOfWork
from services.user_balance import UserBalanceService

logger = logging.getLogger(__name__)


class BalanceMessageConsumer:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self._is_consuming = False

    async def process_message(self, message: AbstractIncomingMessage) -> None:
        try:
            data = json.loads(message.body.decode())
            logger.info(f"Processing message: {data}")
            validated_message = BalanceUpdateMessage.model_validate(data)
        except (json.JSONDecodeError, pydantic.ValidationError) as e:
            logger.error(
                f"Invalid message format: {e}, message body: {message.body}",
                exc_info=True,
            )
            await message.nack(requeue=False)
            return

        try:
            await self._handle_message(validated_message)
            await message.ack()
            logger.info(f"Message processed successfully: {data}")
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            await message.nack(requeue=not message.redelivered)

    async def _handle_message(self, data: BalanceUpdateMessage) -> None:
        async with async_session() as session:
            uow = UnitOfWork(session)
            balance_service = UserBalanceService(uow)
            await balance_service.add_to_balance(
                user_id=data.user_id,
                amount=data.amount,
                transaction_type=data.type,
            )

    async def start_consuming(self) -> None:
        if self._is_consuming:
            logger.warning("Consumer is already running")
            return

        self._is_consuming = True
        logger.info("Starting message consumer...")
        await self.broker.consume(self.process_message)

    async def stop_consuming(self) -> None:
        if not self._is_consuming:
            return

        await self.broker.close()
        logger.info("Message consumer stopped")
