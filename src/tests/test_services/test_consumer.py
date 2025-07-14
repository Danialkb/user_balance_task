import json
import uuid

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from enums import TransactionType
from messaging.consumer.core import BalanceMessageConsumer


def make_message(payload: dict, *, redelivered: bool = False):
    if isinstance(payload, (bytes, bytearray)):
        body = payload
    else:
        body = json.dumps(payload).encode()
    msg = MagicMock()
    msg.body = body
    msg.redelivered = redelivered
    msg.ack = AsyncMock()
    msg.nack = AsyncMock()
    return msg


class DummyBroker:
    async def consume(self, callback):
        self._callback = callback

    async def close(self):
        pass


@pytest.fixture
def broker():
    return DummyBroker()


@pytest.fixture
def consumer(broker) -> BalanceMessageConsumer:
    return BalanceMessageConsumer(broker)


async def test_process_valid_message_calls_service_and_acks(consumer, broker):
    valid_payload = {
        "user_id": str(uuid.uuid4()),
        "amount": 100,
        "type": TransactionType.QUIZ_REWARD.value,
    }
    msg = make_message(valid_payload)

    mock_handle = AsyncMock()
    with patch.object(consumer, '_handle_message', new=mock_handle):
        await consumer.process_message(msg)

        msg.ack.assert_awaited_once()
        msg.nack.assert_not_awaited()


async def test_invalid_json_nacks_without_requeue(consumer):
    msg = make_message(b'not a valid json')
    msg.body = b'not a valid json'

    await consumer.process_message(msg)

    msg.nack.assert_awaited_once_with(requeue=False)
    msg.ack.assert_not_called()


async def test_validation_error_nacks_without_requeue(consumer):
    payload = {"amount": 100}
    msg = make_message(payload)

    await consumer.process_message(msg)

    msg.nack.assert_awaited_once_with(requeue=False)
    msg.ack.assert_not_called()


async def test_unexpected_error_nacks_maybe_requeue(consumer):
    payload = {
        "user_id": str(uuid.uuid4()),
        "amount": 100,
        "type": TransactionType.QUIZ_REWARD.value,
    }

    mock_handle = AsyncMock(side_effect=Exception("Test error"))
    with patch.object(consumer, '_handle_message', new=mock_handle):
        msg = make_message(payload, redelivered=False)
        await consumer.process_message(msg)

        msg.nack.assert_awaited_once_with(requeue=True)
        msg.ack.assert_not_awaited()

        msg = make_message(payload, redelivered=True)
        await consumer.process_message(msg)

        msg.nack.assert_awaited_once_with(requeue=False)
        msg.ack.assert_not_awaited()
