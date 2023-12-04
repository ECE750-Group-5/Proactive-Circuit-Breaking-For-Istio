# Implement the loop with queues

import logging
from queue import Queue, Empty
from sre_parse import State
from threading import Thread
from state import Standby, OverloadingAvoidance, AggressiveProbing
from event import Event, EventFactory


class Analyzer:
    """
    The Analyzer class is responsible for analyzing events and processing them accordingly.

    Attributes:
        event_queue (Queue): A queue to store incoming events.
        plan_queue (Queue): A queue to store plans generated from events.
        event_factory (EventFactory): An event factory to create events.
        services_to_analyze (set): A set of services to be analyzed.
    """

    def __init__(self, event_factory: EventFactory) -> None: 
        self.event_queue = Queue()
        self.plan_queue = Queue()
        self.event_factory = event_factory
        self.services_to_analyze = set()

    def get_plan_queue(self):
        return self.plan_queue     


    def analyze(self) -> None:
        """
        Analyzes events from the event queue and processes them accordingly.
        """
        while True:
            try:
                event = self.event_queue.get(block=True)
                self.process_event(event)
            except Empty:
                logging.info("Event queue is empty.")
                pass
    
    def add_service_to_analyze(self, service_name):
        """
        Adds a service to the set of services to be analyzed.

        Args:
            service_name (str): The name of the service to be added.
        """
        if service_name not in self.services_to_analyze:
            event = self.event_factory.create_event(service_name, Event.STANDBY)
            self.event_queue.put(event)
            logging.info(f"Added service '{service_name}' to be analyzed.")

    def process_event(self, event: Event) -> None:
        """
        Processes an event based on its current state.

        Args:
            event (Event): The event to be processed.
        """
        if event.current_state == Event.STANDBY:
            process_thread = Thread(target=Standby.process, args=(event, self.event_queue, self.event_factory, self.plan_queue))
            process_thread.start()
            logging.info(f"Processing event '{event}' in standby state.")
        elif event.current_state == Event.OVERLOADING_AVOIDANCE:
            process_thread = Thread(target=OverloadingAvoidance.process, args=(event, self.event_queue, self.event_factory, self.plan_queue))
            process_thread.start()
            logging.info(f"Processing event '{event}' in overloading avoidance state.")
        elif event.current_state == Event.AGGRESSIVE_PROBING:
            process_thread = Thread(target=AggressiveProbing.process, args=(event, self.event_queue, self.event_factory, self.plan_queue))
            process_thread.start()
            logging.info(f"Processing event '{event}' in aggressive probing state.")
