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
    
    def __str__(self) -> str:
        return f"Event(timestamp={self.timestamp}, current_state={self.current_state}, metrics={self.metrics}, service_name={self.service_name})"

class EventFactory:
    def __init__(self) -> None:
        pass

    def create_event(self, service_name, current_state):
        cpu_usage_percentage, memory_usage_percentage = MetricsQuerier.query_cpu_and_memory_usage_percentage(service_name)
        metrics = {
            MetricsQuerier.CPU_USAGE_PERCENTAGE: cpu_usage_percentage,
            MetricsQuerier.MEMORY_USAGE_PERCENTAGE: memory_usage_percentage,
        }
        return Event(current_state, metrics, service_name)
        
        

