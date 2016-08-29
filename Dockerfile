FROM rabbitmq:latest

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y \
        python3 python3-setuptools
RUN easy_install3 pip wheel virtualenv

ENV LANG C.UTF-8

RUN mkdir -p /code
WORKDIR /code

ENV WHEELS_ONLY=1
COPY requirements.txt /code/requirements.txt
COPY _deps_python.sh /code/_deps_python.sh
RUN ./_deps_python.sh

COPY entrypoint.sh /code/entrypoint.sh
COPY aioamqp_test_cli.py /code/aioamqp_test_cli.py
COPY aioamqp_test /code/aioamqp_test

ENTRYPOINT ["/code/entrypoint.sh"]
CMD ["run"]
