""" CLI interface to run the client """
import logging
import os

import click

from .client import Client


LOG_FORMAT = ('%(levelname) -7s %(asctime)s %(name) -10s %(funcName) '
              '-10s %(lineno) -4d: %(message)s')


@click.command()
@click.argument('mode', type=click.Choice(('consumer', 'producer')))
@click.option('--host', default='127.0.0.1')
@click.option('--port', default=5672)
@click.option('--username', default='guest')
@click.option('--password', default='guest')
@click.option('--queue', default='aioamqp_test')
@click.option('--exchange', default='aioamqp_test')
@click.option('--pidfile', default='/var/run/{mode}.pid')
@click.option('--debug/--no-debug', default=False)
def cli(mode, host, port, username, password, queue, exchange, pidfile, debug):
    with open(pidfile.format(**locals()), 'w') as handle:
        handle.write('%s' % os.getpid())

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format=LOG_FORMAT)
    logger = logging.getLogger(mode)

    Client(mode, host, port, username, password, queue, exchange, logger).run()
