# AIOAMQP Load Test
Basic load test for Python aioamqp library

- AIOAMQP code: https://github.com/polyconseil/aioamqp
- AIOAMQP docs: https://aioamqp.readthedocs.io/en/latest/

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
    INFO    2016-08-29 06:44:12,769 producer   _rmq_produce  156: 20000 messages sent
    INFO    2016-08-29 06:44:14,297 producer   _rmq_produce  156: 30000 messages sent
    INFO    2016-08-29 06:44:14,348 consumer   _on_message  180: 20000 messages acknowledged

## Stopping

Ctrl+C or any kind of kill signal will cleanly stop all services in Docker, and
both clients.
