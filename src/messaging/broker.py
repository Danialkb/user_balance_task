from typing import Callable, Awaitable, Any

import aio_pika
from aio_pika.abc import (
    AbstractRobustConnection,
    AbstractChannel,
    AbstractExchange,
    AbstractQueue,
    AbstractIncomingMessage,
)

from messaging.config import RabbitConfig


class MessageBroker:
    def __init__(self, config: RabbitConfig, prefetch: int = 1):
        self.config = config
        self.prefetch = prefetch
        self.connection: AbstractRobustConnection | None = None
        self.channel: AbstractChannel | None = None
        self.exchange: AbstractExchange | None = None
        self.queue: AbstractQueue | None = None
        self.dlx_exchange: AbstractExchange | None = None
        self.dlq: AbstractQueue | None = None

    async def connect(self, needs_dlq: bool = True):
        self.connection = await aio_pika.connect_robust(self.config.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=self.prefetch)

        self.exchange = await self.channel.declare_exchange(
            name=self.config.EXCHANGE_NAME,
            type=self.config.EXCHANGE_TYPE,
            durable=True,
            auto_delete=False,
        )

        queue_args = {}
        if needs_dlq:
            queue_args.update(
                {
                    "x-dead-letter-exchange": f"{self.config.EXCHANGE_NAME}.dlx",
                    "x-dead-letter-routing-key": f"{self.config.QUEUE_NAME}.dlq",
                }
            )

        self.queue = await self.channel.declare_queue(
            name=self.config.QUEUE_NAME,
            durable=True,
            arguments=queue_args,
        )

        if needs_dlq:
            await self._setup_dlq()

        await self.queue.bind(self.exchange, self.config.ROUTING_KEY)

    async def _setup_dlq(self):
        self.dlx_exchange = await self.channel.declare_exchange(
            name=f"{self.config.EXCHANGE_NAME}.dlx",
            type="direct",
            durable=True,
            auto_delete=False,
        )

        self.dlq = await self.channel.declare_queue(
            name=f"{self.config.QUEUE_NAME}.dlq",
            durable=True,
        )

        await self.dlq.bind(
            exchange=self.dlx_exchange,
            routing_key=f"{self.config.QUEUE_NAME}.dlq",
        )

    async def consume(
        self,
        callback: Callable[[AbstractIncomingMessage], Awaitable[Any]],
        no_ack: bool = False,
    ):
        if not self.queue:
            raise RuntimeError("Queue not initialized. Call connect() first.")

        await self.queue.consume(callback, no_ack=no_ack)

    async def close(self):
        if not self.connection:
            return

        await self.connection.close()
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
