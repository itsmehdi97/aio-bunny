import abc
import asyncio
import logging
import functools
from typing import List, Callable, TypeVar

import aio_pika
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractConnection
)

from .handler import Handler


_log = logging.getLogger(__name__)


class BaseConsumer(metaclass=abc.ABCMeta):
    _handlers: List[Handler]
    _conn: AbstractConnection

    def __init__(
        self,
        amqp_url: str,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
    ):
        self.url = amqp_url

        self._queue = queue
        self._exchange = exchange
        self._binding_key = binding_key

        self._handlers = []
        self._stopped = False

    def message_handler(
        self,
        queue: str = None,
        exchange: str = None,
        binding_key: str = None,
        prefetch_count: int = 1
    ) -> Callable:
        T = TypeVar("T")

        def decorator(func: Callable[[AbstractIncomingMessage], T]) -> Callable:
            self._handlers.append(
                Handler(
                    func,
                    queue=queue or self._queue,
                    exchange=exchange or self._exchange,
                    binding_key=binding_key or self._binding_key,
                    prefetch_count=prefetch_count))

            @functools.wraps(func)
            def _decorator(msg: AbstractIncomingMessage) -> T:
                return func(msg)
            return _decorator
        return decorator

    @abc.abstractclassmethod
    async def start(self) -> None:
        pass

    @abc.abstractclassmethod
    async def stop(self) -> None:
        pass


class Consumer(BaseConsumer):
    async def start(self) -> None:
        self._conn = await self._connect()
        _log.debug("waiting for messages...")

        [await handler.start(self._conn)
            for handler in self._handlers]

        self._stopped = False

    async def stop(self, timeout: int =None, nowait: bool = False) -> None:
        if self._stopped:
            return

        _log.debug(f"# stopping {len(self._handlers)} handlers...")

        await asyncio.gather(
            *[handler.stop(timeout=timeout, nowait=nowait)
                for handler in self._handlers])
        await self._conn.close()

        self._stopped = True

    async def _connect(self) -> AbstractConnection:
        _log.debug(f"# connecting to {self.url}")
        return await aio_pika.connect_robust(self.url)

    def __del__(self) -> None:
        _log.debug('consumer deleted.')
