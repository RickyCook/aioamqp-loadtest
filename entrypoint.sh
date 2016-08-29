#!/bin/bash
set -e

THIS_DIR="$(cd "$(dirname "$0")"; pwd)"
source "$THIS_DIR/python_env/bin/activate"

if [[ -x "$THIS_DIR/pre-entry.sh" ]]; then
  echo "Sourcing pre-entry script" >&2
  source "$THIS_DIR/pre-entry.sh"
else
  echo "Skipping pre-entry script" >&2
fi

function stopall {
  kill $(cat /var/run/producer.pid) || true
  kill $(cat /var/run/consumer.pid) || true
  rabbitmqctl stop || true
}

case "$1" in
  run)
    trap 'stopall' SIGINT SIGQUIT SIGTERM

    docker-entrypoint.sh rabbitmq-server &
    "$THIS_DIR/aioamqp_loadtest_cli.py" producer &
    producer_pid=$!
    "$THIS_DIR/aioamqp_loadtest_cli.py" consumer &
    consumer_pid=$!

    wait $producer_pid
    wait $consumer_pid
    ;;
  *) "$@" ;;
esac
