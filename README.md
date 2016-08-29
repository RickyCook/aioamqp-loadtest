# AIOAMQP Load Test
Basic load test for Python aioamqp library

## Running (Docker)

Build the image

    $ docker build -t aioamqp_test .
    ...
    Successfully built deadbeefdead

Run the built image

    $ docker run -it --rm aioamqp_test
    ...
    INFO    2016-08-29 06:44:11,446 producer   _rmq_produce  156: 10000 messages sent
    INFO    2016-08-29 06:44:12,259 consumer   _on_message  180: 10000 messages acknowledged

## Stopping

Ctrl+C or any kind of kill signal will cleanly stop all services in Docker, and
both clients.
