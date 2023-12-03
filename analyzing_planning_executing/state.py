from abc import ABC, abstractmethod
import json
import queue
from event import EventFactory, Event
from metrics_querier import MetricsQuerier
from plan import Plan
from subprocess import PIPE, run

class State:
    def __init__(self) -> None:
        pass

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        pass

    @staticmethod
    def transit_to(service_name:str, next_state, event_queue: queue.Queue, event_factory: EventFactory):
        event = event_factory.create_event(service_name, next_state)
        event_queue.put(event)
    
    @staticmethod
    def get_currency_limit(service_name):
        destination_rule_query = f"kubectl get destinationrule {service_name} -o json"
        destination_rule_json_str = run(destination_rule_query, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout
        destination_rule_json = json.loads(destination_rule_json_str)
        concurrency_limit = destination_rule_json["spec"]["trafficPolicy"]["connectionPool"]["http"]["http1MaxPendingRequests"]
        return int(concurrency_limit)



class Standby(State):
    def __init__(self) -> None:
        pass

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]
        while True:
            if cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9:
                Standby.transit_to(event.service_name, Event.OVERLOADING_AVOIDANCE, event_queue, event_factory)
                break
            elif cpu_usage_percentage < 0.8 and memory_usage_percentage < 0.8:
                Standby.transit_to(event.service_name, Event.AGGRESSIVE_PROBING, event_queue, event_factory)
                break
            
            cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(event.service_name)
            memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(event.service_name)

        
        
        

class OverloadingAvoidance(State):
    def __init__(self) -> None:
        pass

    @staticmethod
    def triple_limit():
        pass

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]
        while True:
            if cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9:
                plan_queue.put(Plan(Plan.ACTION_RAISE_LIMIT))
            elif cpu_usage_percentage < 0.9 and memory_usage_percentage < 0.9:
                OverloadingAvoidance.transit_to(event.service_name, Event.STANDBY, event_queue, event_factory)
                break
            elif cpu_usage_percentage < 0.8 and memory_usage_percentage < 0.8:
                OverloadingAvoidance.transit_to(event.service_name, Event.AGGRESSIVE_PROBING, event_queue, event_factory)
                break
            cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(event.service_name)
            memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(event.service_name)




class AggressiveProbing(State):
    def __init__(self) -> None:
        pass

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]


if __name__ == "__main__":
    print(State.get_currency_limit("httpbin"))