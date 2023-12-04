import logging
import queue
import random
from event import EventFactory, Event
from metrics_querier import MetricsQuerier
from plan import Plan
from concurrency_limit_querier import ConcurrencyLimitQuerier


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
        logging.info(f"Transit to {next_state} state for service {service_name}")


def get_prob_flag(prob):
    upper_limit = prob * 100
    randomInt = random.randint(0, 99)
    return randomInt < upper_limit


class Standby(State):
    """
    Represents the standby state of the system.

    Attributes:
        None

    Methods:
        get_setting_limit_plan(service_name): Returns a plan to set the concurrency limit based on metrics.
        process(event, event_queue, event_factory, plan_queue): Processes the event and determines the appropriate action based on CPU and memory usage.
    """
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_setting_limit_plan(service_name):
        """
        Returns a plan to set the concurrency limit based on metrics.

        Args:
            service_name (str): The name of the service.

        Returns:
            Plan: The plan to set the concurrency limit.
        """
        non_500_non_0_latency = MetricsQuerier.query_average_non_500_non_0_latency_seconds(service_name)
        non_500_non_0_arrival_rate = MetricsQuerier.query_average_non_500_non_0_arrival_rate(service_name)
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        logging.info(f"non_500_non_0_latency: {non_500_non_0_latency}, non_500_non_0_arrival_rate: {non_500_non_0_arrival_rate}")
        if non_500_non_0_latency == 0 or non_500_non_0_arrival_rate == 0:
            return Plan(service_name, Plan.ACTION_SET_LIMIT, old_limit, old_limit)
        new_limit = int(non_500_non_0_arrival_rate * non_500_non_0_latency)
        return Plan(service_name, Plan.ACTION_SET_LIMIT, old_limit, new_limit)

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        """
        Process the event and determine the appropriate action based on CPU and memory usage.

        Args:
            event (Event): The event to be processed.
            event_queue (Queue): The queue to store events.
            event_factory (EventFactory): The event factory to create new events.
            plan_queue (Queue): The queue to store plans.

        Returns:
            None
        """
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]
        while True:
            if cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9:
                plan = Standby.get_setting_limit_plan(event.service_name)
                logging.info(f"Plan: {plan}")
                plan_queue.put(plan)
                Standby.transit_to(event.service_name, Event.OVERLOADING_AVOIDANCE, event_queue, event_factory)
                break
            elif cpu_usage_percentage < 0.8 and memory_usage_percentage < 0.8:
                if get_prob_flag(0.5):
                    Standby.transit_to(event.service_name, Event.AGGRESSIVE_PROBING, event_queue, event_factory)
                    break
            
            cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(event.service_name)
            memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(event.service_name)
            


class OverloadingAvoidance(State):
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_lower_limit_plan(service_name):
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        new_limit = int(0.75 * old_limit + 1)
        return Plan(service_name, Plan.ACTION_LOWER_LIMIT, old_limit, new_limit)

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]
        while True:
            if cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9:
                plan = OverloadingAvoidance.get_lower_limit_plan(event.service_name)
                plan_queue.put(plan)
                logging.info(f"Plan: {plan}")
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

    def get_raise_limit_plan(service_name):
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        new_limit = 2 * old_limit
        return Plan(service_name, Plan.ACTION_RAISE_LIMIT, old_limit, new_limit)

    @staticmethod
    def process(event, event_queue, event_factory, plan_queue):
        cpu_usage_percentage = event.metrics[MetricsQuerier.CPU_USAGE_PERCENTAGE]
        memory_usage_percentage = event.metrics[MetricsQuerier.MEMORY_USAGE_PERCENTAGE]
        while True:
            if cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9:
                plan = Standby.get_setting_limit_plan(event.service_name)
                plan_queue.put(plan)
                AggressiveProbing.transit_to(event.service_name, Event.OVERLOADING_AVOIDANCE, event_queue, event_factory)
                break
            elif cpu_usage_percentage < 0.8 and memory_usage_percentage < 0.8:
                if get_prob_flag(0.5):
                    plan = AggressiveProbing.get_raise_limit_plan(event.service_name)
                    plan_queue.put(plan)
                else:
                    AggressiveProbing.transit_to(event.service_name, Event.STANDBY, event_queue, event_factory)
                    break
