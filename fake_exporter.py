from logging import INFO, getLogger, StreamHandler
from random import random
from signal import signal, SIGINT, SIGTERM
from sys import argv
from time import sleep

import requests
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily, REGISTRY


logHandler = StreamHandler()

log = getLogger(__name__)
log.setLevel(INFO)
log.addHandler(logHandler)

good_counter = 0
bad_counter = 0


class FakeMetricsCollector:
    def __init__(self):
        pass
    def collect(self):
        global good_counter, bad_counter

        good_counter += round(random()*1000)
        bad_counter += round(random()*40)

        counter = CounterMetricFamily("fake_http_requests_total", "FAKE", labels=['type', 'service'])
        counter.add_metric(value=good_counter, labels=["good", "server1"])
        counter.add_metric(value=good_counter+bad_counter, labels=["total", "server1"])

        return [counter]


class SignalHandler:
    def __init__(self):
        self.shutdown = False

        # Register signal handler
        signal(SIGINT, self._on_signal_received)
        signal(SIGTERM, self._on_signal_received)

    def is_shutting_down(self):
        return self.shutdown

    def _on_signal_received(self, _signal, _frame):
        log.info("Exporter is shutting down")
        self.shutdown = True


if __name__ == "__main__":
    # Init logger
    # Register signal handler
    signal_handler = SignalHandler()

    # Register our custom collector
    log.info("Exporter is starting up")
    REGISTRY.register(FakeMetricsCollector())

    # Start server
    start_http_server(10000)
    log.info(f"Exporter listening on port 10000")

    while not signal_handler.is_shutting_down():
        sleep(1)

    log.info("Exporter has shutdown")
