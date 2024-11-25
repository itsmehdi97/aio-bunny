import asyncio
import functools
from typing import Callable, Optional, TypeAlias, TypeVar, List, Dict
import logging

import aio_pika
from aio_pika.abc import AbstractConnection, AbstractIncomingMessage

from .consumer import Consumer
from .publisher import Publisher
from .exchange_types import RabbitExchangeType
from .log import get_logger


log = get_logger(__name__)
Arguments: TypeAlias = Dict[str, str | int | None]
T = TypeVar("T")


class Bunny:
    _conn: AbstractConnection

    def __init__(self, amqp_url: str) -> None:
        self.url = amqp_url

        self._consumers: List[Consumer] = []
        self._publishers: List[Publisher] = []
        self._conn: AbstractConnection = None

    async def _connect(self) -> None:
        self._conn = await aio_pika.connect_robust(self.url, reconnect_interval=5, fail_fast=False)

    async def connect(self, timeout: float = 25.0) -> None:
        try:
            await asyncio.wait_for(self._connect(), timeout=timeout)
        except TimeoutError:
            raise Exception("failed to connect to Rabbitmq server.")

        logging.info("connection to rabbitmq server stablished")

    async def start(self) -> None:
        if not self._conn:
            raise ValueError("connection to Rabbitmq server not stablished."
                             " ensure 'connect' method is awaited before starting consumers.")

        log.debug("Starting publishers")
        await asyncio.gather(
            *[publisher.start(self._conn) for publisher in self._publishers])

        log.debug("Starting consumers")
        asyncio.gather(
            *[consumer.start(self._conn) for consumer in self._consumers])

    async def stop(self, timeout: int = None, nowait: bool = False) -> None:
        log.debug("Stopping consumers")
        await asyncio.gather(
            *[consumer.stop(timeout=timeout, nowait=nowait)
                for consumer in self._consumers])

    def consumer(
        self,
        queue: str,
        exchange: str,
        exchange_type: RabbitExchangeType = RabbitExchangeType.DIRECT,
        routing_key: Optional[str] = None,
        prefetch_count: Optional[int] = None,
        auto_ack: bool = False,
        consumer_arguments: Optional[Arguments] = None,

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
    ) -> Callable:
        def decorator(func: Callable[[AbstractIncomingMessage], T]) -> Callable:
            self._consumers.append(
                Consumer(
                    func,
                    queue,
                    exchange,
                    exchange_type,
                    routing_key or exchange,
                    prefetch_count=prefetch_count,
                    auto_ack=auto_ack,
                    arguments=consumer_arguments,

                    queue_durable=queue_durable,
                    queue_auto_delete=queue_auto_delete,
                    queue_passive=queue_passive,
                    queue_exclusive=queue_exclusive,
                    queue_arguments=queue_arguments,

                    exchange_durable=exchange_durable,
                    exchange_auto_delete=exchange_auto_delete,
                    exchange_internal=exchange_internal,
                    exchange_passive=exchange_passive,
                    exchange_arguments=exchange_arguments))

            @functools.wraps(func)
            def _decorator(msg: AbstractIncomingMessage) -> T:
                return func(msg)

            return _decorator
        return decorator

    def publisher(
        self,
        exchange: str,
        exchange_type: RabbitExchangeType = RabbitExchangeType.DIRECT,
        exchange_durable: bool = False,
        exchange_auto_delete: bool = False,
        exchange_internal: bool = False,
        exchange_passive: bool = False,
        exchange_arguments: Optional[Arguments] = None,
        default_routing_key: str = None,
    ) -> Publisher:
        publisher = Publisher(
            exchange,
            exchange_type,
            exchange_durable=exchange_durable,
            exchange_auto_delete=exchange_auto_delete,
            exchange_internal=exchange_internal,
            exchange_passive=exchange_passive,
            exchange_arguments=exchange_arguments,
            default_routing_key=default_routing_key)

        self._publishers.append(publisher)
        return publisher
