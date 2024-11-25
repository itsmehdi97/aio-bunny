from aio_pika.exceptions import (
    AMQPChannelError, AMQPConnectionError, AuthenticationError, ChannelClosed,
    ChannelInvalidStateError,
    ChannelNotFoundEntity, IncompatibleProtocolError,
    MethodNotImplemented, ProbableAuthenticationError,
    QueueEmpty
)


class ExchangeNotFound(ChannelNotFoundEntity):
    pass


__all__ = (
    "AMQPChannelError",
    "AMQPConnectionError",
    "AuthenticationError",
    "ChannelClosed",
    "ChannelInvalidStateError",
    "ChannelNotFoundEntity",
    "IncompatibleProtocolError",
    "MethodNotImplemented",
    "ProbableAuthenticationError",
    "QueueEmpty",
    "ExchangeNotFound",
)
