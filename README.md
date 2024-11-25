## aio-bunny

An asyncio compatible wrapper around aio-pika that brings the follwoing advantages:
- [x] **Simplified API**: Abstracts the complexity of defining queues and exchanges, making it easy to set up consumer/producers.
- [x] **Graceful Consumer Shutdown**: Provides an API to stop consumers without disrupting unacknowledged tasks, ensuring a smooth and safe shutdown process.
- [ ] **Idempotent Consumers**: Offers a straightforward API for integrating with external databases (e.g., Redis, MySQL) to ensure idempotency. As recommended in the [RabbitMQ documentation](https://www.rabbitmq.com/docs/confirms#automatic-requeueing), consumers configured with manual acknowledgment and concerned about avoiding duplicate message processing should implement idempotency.
- [ ] **Prometheus Integration**: Integrates with Prometheus to collect useful metrics for monitoring the state of consumers and producers. You can easily choose to enable metric collection based on your needs.


### Installation
```
pip install aio-bunny
```
### Usage examples
In the simplest form, you can do the following to spin up a consumer:
``` python
import asyncio

from aio_bunny import Bunny, IncomingMessage


async def main():
    bunny = Bunny("amqp://guest:guest@127.0.0.1/")
    await bunny.connect()

    @bunny.consumer(
        queue="myqueue",
        exchange="myexchange",
        routing_key="key")
    async def on_message(msg: IncomingMessage):
        await asyncio.sleep(1)
        print('received:', msg.body.decode())


    await bunny.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
```
\
To shutdown the consumers gracefully, all you need to do is to call the `stop` method on the `Bunny` instance. \
This method will prevent the consumer from accepting new messages from the broker, waits for all inflight tasks to finish and exits cleanly.\

So In the following example, we want to stop the application whenever `SIGINT` OR `SIGTERM` is received:
``` python
import asyncio
import signal

from aio_bunny import Bunny, IncomingMessage


async def main():
    bunny = Bunny("amqp://guest:guest@127.0.0.1/")
    await bunny.connect()

    async def shutdown(signal, loop):
        print(f"Received exit signal: {signal.name}")
        await bunny.stop()  # Stopping the consumers here
        loop.stop()

    loop = asyncio.get_event_loop()
    # Call the shutdown funciton on any of these signals.
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(s, lambda s=s: asyncio.create_task(shutdown(s, loop)))

    @bunny.consumer(
        queue="myqueue",
        exchange="myexchange",
        routing_key="key")
    async def on_message(msg: IncomingMessage):
        await asyncio.sleep(1)
        print('received:', msg.body.decode())


    await bunny.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
```
And the following shows how to set up a publisher:
``` python
import asyncio

from aio_bunny import Bunny, Message


async def main():
    bunny = Bunny("amqp://guest:guest@127.0.0.1/")
    await bunny.connect()

    # init a new publisher instance
    publisher = bunny.publisher(
        "exchange_name",
        exchange_type=RabbitExchangeType.DIRECT,
        exchange_durable=True)

    # publish a message
    await publisher.publish(Message("some message!"), routing_key="key")



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
```
## Versioning
This software follows [Semantic Versioning](https://semver.org/)
### Development

#### Setting up development environment
Clone the project:
```
git clone repo_url
cd aio-bunny
```
Create a virtualenv for `aio-bunny`:
```
python3 -m venv venv
source venv/bin/activate
```
Install the requirements:
```
pip install -e '.[develop]'
```