import uuid
import logging
from typing import Callable, Any

from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractConnection,
    AbstractQueue,
    AbstractChannel,
    AbstractExchange
)


_log = logging.getLogger(__name__)


class Handler:
    queue: AbstractQueue
    exchange: AbstractExchange
    _ctag: str
    _name: str

    def __init__(
        self,
        cb: Callable[[AbstractIncomingMessage], Any],
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
        prefetch_count: int = 1
    ):
        self._ready = False
        self._name = cb.__name__

        self._queue = queue or uuid.uuid4().hex
        self._exchange = exchange
        self._binding_key = binding_key or exchange
        self.prefetch_count = prefetch_count
        self.cb = cb

    @property
    def ready(self) -> bool:
        return self._ready

    async def setup(
            self, channel: AbstractChannel
            ) -> AbstractQueue:
        # TODO: handle signature conflicts.
        _log.debug(f"# setting up handler {self._name}")

        queue = await channel.declare_queue(self._queue)
        if self._exchange:
            exchange = await channel.declare_exchange(self._exchange)
            await queue.bind(exchange, routing_key=self._binding_key)

        await channel.set_qos(prefetch_count=self.prefetch_count)

        self._ready = True
        return queue

    async def start(self, conn: AbstractConnection) -> None:
        channel = await conn.channel()
        self.queue = await self.setup(channel)
        self._ctag = await self.queue.consume(self.cb)

    async def stop(self, timeout: int = None, nowait: bool = False) -> None:
        await self.queue.cancel(
            self._ctag, timeout=timeout, nowait=nowait)

    def __repr__(self) -> str:
        return f"{self._name} -> queue:{self._queue}\n" + \
            "bindingkey:{self.binding_key}\n" + \
            "exchange:{self._exchange}"
