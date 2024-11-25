import asyncio
from typing import Optional, Callable, Any, TypeAlias, Dict, List

from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractConnection,
    AbstractQueue,
    AbstractChannel,
)

from .exchange_types import RabbitExchangeType
from .log import get_logger


log = get_logger(__name__)
Arguments: TypeAlias = Dict[str, str | int | None]


class Consumer:
    def __init__(
        self,
        callback: Callable[[AbstractIncomingMessage], Any],
        queue: str,
        exchange: str,
        exchange_type: RabbitExchangeType,
        routing_key: str,
        prefetch_count: Optional[int] = None,
        auto_ack: bool = False,
        arguments: Optional[Arguments] = None,

        queue_durable: bool = False,
        queue_auto_delete: bool = False,
        queue_passive: bool = False,
        queue_exclusive: bool = False,
        queue_arguments: Optional[Arguments] = None,

        exchange_durable: bool = False,
        exchange_auto_delete: bool = False,
        exchange_internal: bool = False,
        exchange_passive: bool = False,
        exchange_arguments: Optional[Arguments] = None,
    ) -> None:

        self.cb = callback
        self.queue_name = queue
        self.exchange_name = exchange
        self.exchange_type = exchange_type.value
        self.routing_key = routing_key
        self.prefetch_count = prefetch_count
        self.auto_ack = auto_ack
        self.arguments = arguments

        self._queue_args = {
            'durable': queue_durable,
            'auto_delete': queue_auto_delete,
            'passive': queue_passive,
            'exclusive': queue_exclusive,
            'arguments': queue_arguments,
        }
        self._exchange_args = {
            'durable': exchange_durable,
            'auto_delete': exchange_auto_delete,
            'internal': exchange_internal,
            'passive': exchange_passive,
            'arguments': exchange_arguments,
        }

        self.consumer_tag: str = ""
        self._queue: Optional[AbstractQueue] = None

    async def setup(self, channel: AbstractChannel) -> AbstractQueue:
        if self.prefetch_count:
            await channel.set_qos(self.prefetch_count)

        exchange = await channel.declare_exchange(
            self.exchange_name,
            self.exchange_type,
            **self._exchange_args)  # type: ignore
        queue = await channel.declare_queue(
            self.queue_name,
            **self._queue_args)  # type: ignore
        await queue.bind(exchange, self.routing_key)

        return queue

    async def _wrapped_callback(self, msg: AbstractIncomingMessage) -> Any:
        async with msg.process():
            return await self.cb(msg)

    async def start(self, conn: AbstractConnection) -> str:
        channel = await conn.channel()
        self._queue = await self.setup(channel)

        self._running_tasks: set = set()

        log.debug("Start to consuming queue: %s", self.queue_name)
        async with self._queue.iterator(
            no_ack=self.auto_ack, arguments=self.arguments
        ) as queue_iterator:
            self.consumer_tag = queue_iterator._consumer_tag

            async for msg in queue_iterator:
                task = asyncio.create_task(self._wrapped_callback(msg))
                task.add_done_callback(self._running_tasks.discard)
                self._running_tasks.add(task)

        return self.consumer_tag

    async def stop(
        self, timeout: Optional[int] = None, nowait: bool = False
    ) -> List[Exception | None]:
        if not self._queue:
            log.debug("Consumer object has not been started correctly.")
            return []

        await self._queue.cancel(
            self.consumer_tag, timeout=timeout, nowait=nowait)

        log.debug("Consumer %s canceled. Waiting for tasks to finish.", self.consumer_tag)

        return await asyncio.gather(*self._running_tasks, return_exceptions=True)
