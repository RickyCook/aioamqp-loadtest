""" Setup and run the client for producing or consuming messages """
import asyncio
import signal

from concurrent import futures

import aioamqp

from aioamqp.exceptions import AmqpClosedConnection


RECONNECT_TIMER = 5


class Client(object):
    """ Daemon to take jobs from RabbitMQ and start workers for them """

    def __init__(self, mode, host, port, username, password, queue, exchange, logger):
        self._mode = mode
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._queue = queue
        self._exchange = exchange
        self._logger = logger
        self._transport = None
        self._init_future = None
        self._shutting_down = False
        self._message_count = 0

    def run(self):
        """ Connect and run the event loop """
        loop = asyncio.get_event_loop()
        self._init_future = self._rmq_init()
        loop.add_signal_handler(signal.SIGINT, self.shutdown)
        loop.add_signal_handler(signal.SIGTERM, self.shutdown)
        loop.run_until_complete(self._init_future)
        loop.run_forever()

    def shutdown(self):
        """ Perform a graceful shutdown """
        asyncio.async(self._shutdown_coro())

    @asyncio.coroutine
    def _shutdown_coro(self):
        """ Shutdown when there is no job running """
        self._logger.info('Shutting down now')
        asyncio.get_event_loop().stop()

    @asyncio.coroutine
    def _rmq_init(self):
        """ Connect, declare, bind, consume/produce. Retry on failure """
        while True:
            if self._transport is not None:
                self._transport.close()

            try:
                self._logger.info('Connecting to RabbitMQ')
                self._transport, protocol = yield from asyncio.wait_for(
                    aioamqp.connect(
                        self._host,
                        self._port,
                        self._username,
                        self._password,
                        on_error=self._on_connect_error,
                    ),
                    timeout=30,
                )

                self._logger.info('Creating channel')
                channel = yield from protocol.channel()

                self._logger.info(
                    'Declaring exchange "%s"', self._exchange,
                )
                yield from channel.exchange_declare(
                    self._exchange,
                    type_name='fanout',
                )

                self._logger.info(
                    'Declaring queue "%s"', self._queue,
                )
                yield from channel.queue_declare(
                    self._queue,
                    exclusive=False,
                )

                if self._mode == 'consumer':
                    self._logger.debug('Setting prefetch')
                    yield from channel.basic_qos(prefetch_count=1, prefetch_size=0)

                    self._logger.info('Binding queue')
                    yield from channel.queue_bind(
                        self._queue,
                        self._exchange,
                        '*',
                    )

                break  # Break out of inifinite loop

            except (
                OSError,
                AmqpClosedConnection,
                aioamqp.exceptions.ChannelClosed,
                futures.TimeoutError,
            ) as err:
                if isinstance(err, futures.TimeoutError):
                    self._logger.error('Timed out')
                else:
                    try:
                        self._logger.error(err.message)
                    except AttributeError:
                        self._logger.error(err)

                self._logger.info(
                    'Reconnecting in %d seconds', RECONNECT_TIMER
                )
                yield from asyncio.sleep(RECONNECT_TIMER)

        self._init_future = None

        if self._mode == 'consumer':
            asyncio.async(self._rmq_consume(channel))
        elif self._mode == 'producer':
            # Can be doing more producing while yielded
            for _ in range(100):
                asyncio.async(self._rmq_produce(channel))

    @asyncio.coroutine
    def _on_connect_error(self, err):
        """ Log errors, and try to reinit if that's not already happening """
        try:
            self._logger.error(err.message)
        except AttributeError:
            self._logger.error(err)

        if self._init_future is None:
            self._init_future = self._rmq_init()
            asyncio.async(self._init_future)

    ###### PRODUCER ######

    @asyncio.coroutine
    def _rmq_produce(self, channel):
        """ Start to produce messages, updating count """
        try:
            yield from channel.basic_publish(
                'message',
                exchange_name=self._exchange,
                routing_key='',
            )
            self._message_count += 1
            if self._message_count % 10000 == 0:
                self._logger.info("%s messages sent", self._message_count)
        finally:
            asyncio.async(self._rmq_produce(channel))

    ###### CONSUMER ######

    @asyncio.coroutine
    def _rmq_consume(self, channel):
        """ Start to consume messages """
        try:
            yield from channel.basic_consume(
                self._on_message,
                queue_name=self._queue,
            )
        finally:
            asyncio.async(self._rmq_consume(channel))

    def _on_message(self, channel, body, envelope, properties):
        """ Ack the message, and update count """
        yield from channel.basic_client_ack(
            delivery_tag=envelope.delivery_tag,
        )
        self._message_count += 1
        if self._message_count % 10000 == 0:
            self._logger.info("%s messages acknowledged", self._message_count)
