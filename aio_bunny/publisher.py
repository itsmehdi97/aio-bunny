from typing import TypeAlias, Dict, Optional

from aio_pika import Message
from aio_pika.abc import AbstractExchange, AbstractChannel, AbstractConnection

from .exchange_types import RabbitExchangeType


Arguments: TypeAlias = Dict[str, str | int | None]


class Publisher:
    def __init__(
        self,
        exchange: str,
        exchange_type: RabbitExchangeType,
        exchange_durable: bool = False,
        exchange_auto_delete: bool = False,
        exchange_internal: bool = False,
        exchange_passive: bool = False,
        exchange_arguments: Optional[Arguments] = None,
        default_routing_key: str = None,
    ) -> None:
        self.exchange = exchange
        self.exchange_type = exchange_type
        self.default_routing_key = default_routing_key
        self._exchange_args = {
            'durable': exchange_durable,
            'auto_delete': exchange_auto_delete,
            'internal': exchange_internal,
            'passive': exchange_passive,
            'arguments': exchange_arguments,
        }

        self._exchange: AbstractExchange

    async def publish(
        self,
        msg: Message,
        routing_key: str = None,
        mandatory: bool = True,
        immediate: bool = False,
    ) -> None:
        await self._exchange.publish(
            msg, routing_key or self.default_routing_key, mandatory=mandatory, immediate=immediate)

    async def start(self, conn: AbstractConnection) -> None:
        channel = await conn.channel()
        self._exchange = await self.setup(channel)

    async def setup(self, channel: AbstractChannel) -> AbstractExchange:
        return await channel.declare_exchange(
            self.exchange,
            self.exchange_type.value,
            **self._exchange_args)  # type: ignore
