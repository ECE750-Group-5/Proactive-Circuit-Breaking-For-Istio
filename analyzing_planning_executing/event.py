import time
from metrics_querier import MetricsQuerier

class Event:
    STANDBY = 0
    OVERLOADING_AVOIDANCE = 1
    AGGRESSIVE_PROBING = 2
    def __init__(self, current_state: int, metrics: dict, service_name) -> None:
        self.timestamp = time.time()
        self.current_state = current_state
        self.metrics = metrics
        self.service_name = service_name


class EventFactory:
    def __init__(self, prometheus_url) -> None:
        self.metrics_querier = MetricsQuerier(prometheus_url)

    def create_event(self, service_name, current_state):
        cpu_usage_percentage, memory_usage_percentage, non_500_non_0_latency_seconds, non_500_non_0_arrival_rate = self.metrics_querier.query_metrics(service_name)
        metrics = {
            MetricsQuerier.CPU_USAGE_PERCENTAGE: cpu_usage_percentage,
            MetricsQuerier.MEMORY_USAGE_PERCENTAGE: memory_usage_percentage,
            MetricsQuerier.NON_500_NON_0_LATENCY: non_500_non_0_latency_seconds,
            MetricsQuerier.NON_500_NON_0_ARRIVAL_RATE: non_500_non_0_arrival_rate
        }
        return Event(current_state, metrics, service_name)
        
        

