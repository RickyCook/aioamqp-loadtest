# AIOAMQP Load Test
Basic load test for Python aioamqp library

- AIOAMQP code: https://github.com/polyconseil/aioamqp
- AIOAMQP docs: https://aioamqp.readthedocs.io/en/latest/

## Running (Docker)

The Dockerfile provided runs a RabbitMQ server, a producer, and a consumer that
all interact correctly with each other.

    $ docker run -it --rm thatpanda/aioamqp-loadtest:latest
    ...
    INFO    2016-08-29 06:44:11,446 producer   _rmq_produce  156: 10000 messages sent
    INFO    2016-08-29 06:44:12,259 consumer   _on_message  180: 10000 messages acknowledged
    INFO    2016-08-29 06:44:12,769 producer   _rmq_produce  156: 20000 messages sent
    INFO    2016-08-29 06:44:14,297 producer   _rmq_produce  156: 30000 messages sent
    INFO    2016-08-29 06:44:14,348 consumer   _on_message  180: 20000 messages acknowledged

*Optionally*, you can also build the Docker image locally. If you don't do this,
the auto-built image from Docker Hub will be pulled and should be exactly the
same.

    $ docker build -t thatpanda/aioamqp-loadtest:latest .
    ...
    Successfully built deadbeefdead

## Stopping

Ctrl+C or any kind of kill signal will cleanly stop all services in Docker, and
both clients.
