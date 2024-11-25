from enum import Enum


class RabbitExchangeType(str, Enum):
    DIRECT = "direct"
    FANOUT = "fanout"
    TOPIC = "topic"
    HEADERS = "headers"
    X_DELAYED_MESSAGE = "x-delayed-message"
