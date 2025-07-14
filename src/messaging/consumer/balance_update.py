import asyncio
import logging
import logging.config

from messaging.config import RabbitConfig

from messaging.broker import MessageBroker
from messaging.consumer.core import BalanceMessageConsumer
from resources.config import settings
from resources.logs.config import logging_config

logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)


async def main():
    config = RabbitConfig(
        RABBITMQ_URL=settings.RABBITMQ_URL,
        EXCHANGE_NAME=settings.BALANCE_EXCHANGE,
        EXCHANGE_TYPE=settings.BALANCE_EXCHANGE_TYPE,
        QUEUE_NAME=settings.BALANCE_QUEUE,
        ROUTING_KEY=settings.BALANCE_ROUTING_KEY,
    )

    broker = MessageBroker(config)
    consumer = BalanceMessageConsumer(broker)
    try:
        await broker.connect()
        logger.info("Consumer started")
        await consumer.start_consuming()

        stop_event = asyncio.Event()
        await stop_event.wait()
    except asyncio.CancelledError:
        logger.info("Consumer stopped gracefully")
    finally:
        await consumer.stop_consuming()


if __name__ == "__main__":
    asyncio.run(main())
