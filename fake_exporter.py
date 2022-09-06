from logging import INFO, getLogger, StreamHandler
from random import random
from signal import signal, SIGINT, SIGTERM
from sys import argv
from time import sleep

import requests
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from pythonjsonlogger import jsonlogger


logHandler = StreamHandler()

log = getLogger(__name__)
log.setLevel(INFO)
log.addHandler(logHandler)


class FakeMetricsCollector:
    def __init__(self):
        pass
    def collect(self):
        good_metrics = random()*100
        pass_slo_metrics_bad = good_metrics / (110 + random()*20)
        failed_slo_metrics_total = good_metrics + good_metrics / 2

        gauge = GaugeMetricFamily("http_requests", "This is just for testing HPA", labels=['type', 'service'])
        gauge.add_metric(value=good_metrics, labels=["good", "passing_service"])
        gauge.add_metric(value=pass_slo_metrics_bad, labels=["bad", "passing_service"])

        # gauge.add_metric(value=good_metrics, labels=["good", "failing_service"])
        # gauge.add_metric(value=failed_slo_metrics_total, labels=["total", "failing_service"])

        return [gauge]


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
