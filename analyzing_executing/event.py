class EventFactory:
    def __init__(self, prometheus_url) -> None:
        self.metrics_querier = MetricsQuerier(prometheus_url)

    def create_event(self, service_name, current_state) -> Event:
        cpu_usage_percentage, memory_usage_percentage, non_500_rate, p99_latency_seconds = self.metrics_querier.query_metrics(service_name)
        metrics = {
            MetricsQuerier.CPU: cpu_usage_percentage,
            "memory_usage_percentage": memory_usage_percentage,
            "non_500_rate": non_500_rate,
            "p99_latency_seconds": p99_latency_seconds
        }
        
        

class Event:
    START = 0
    OVERLOADING_AVOIDANCE = 1
    AGGRESSIVE_PROBING = 2
    def __init__(self, current_state: int, metrics: dict, service_name) -> None:
        self.timestamp = time.time()
        self.current_state = current_state
        self.metrics = data
        self.service_name = service_name