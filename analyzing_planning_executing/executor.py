import logging
from queue import Empty
from threading import Thread
from concurrency_limit_querier import ConcurrencyLimitQuerier
from concurrency_limit_setter import ConcurrencyLimitSetter
from metrics_querier import MetricsQuerier

from plan import Plan



class Executor:
    """
    Executes plans from a plan queue.
    """

    def __init__(self, plan_queue):
        self.plan_queue = plan_queue
    
    def execute(self):
        while True:
            try:
                plan = self.plan_queue.get(block=True)
                logging.info(f"Executing plan: {plan}")
                processing_thread = Thread(target=Executor.process_plan, args=(plan,))
                processing_thread.start()
            except Empty:
                pass
    
    @staticmethod
    def process_plan(plan):
        logging.info(f"Processing plan: {plan}")
        if plan.get_action() == Plan.ACTION_RAISE_LIMIT:
            Executor.execute_raise_limit(plan)
        elif plan.get_action() == Plan.ACTION_LOWER_LIMIT:
            logging.info("lowering limit")
            Executor.execute_lower_limit(plan)
        elif plan.get_action() == Plan.ACTION_SET_LIMIT:
            Executor.execute_set_limit(plan)
    
    @staticmethod
    def execute_raise_limit(plan):
        old_limit_expected = plan.get_old_limit()
        new_limit = plan.get_new_limit()
        service_name = plan.get_service_name()
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(service_name)
        memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(service_name)
        if old_limit == old_limit_expected and (cpu_usage_percentage < 0.8 and memory_usage_percentage < 0.8) and old_limit < new_limit:
            ConcurrencyLimitSetter.set_concurrency_limit(service_name, new_limit)
            logging.info(f"Concurrency limit raised for service {service_name}. New limit: {new_limit}")
        
    @staticmethod
    def execute_set_limit(plan):
        old_limit_expected = plan.get_old_limit()
        new_limit = plan.get_new_limit()
        service_name = plan.get_service_name()
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        if old_limit == old_limit_expected and old_limit != new_limit:
            ConcurrencyLimitSetter.set_concurrency_limit(service_name, new_limit)
            logging.info(f"Concurrency limit set for service {service_name}. New limit: {new_limit}")
    
    @staticmethod
    def execute_lower_limit(plan):
        old_limit_expected = plan.get_old_limit()
        new_limit = plan.get_new_limit()
        service_name = plan.get_service_name()
        old_limit = ConcurrencyLimitQuerier.query_concurrency_limit(service_name)
        cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(service_name)
        memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(service_name)
        logging.info(f"old_limit: {old_limit}, cpu_usage_percentage: {cpu_usage_percentage}, memory_usage_percentage: {memory_usage_percentage}")
        if old_limit == old_limit_expected and (cpu_usage_percentage > 0.9 or memory_usage_percentage > 0.9) and old_limit > new_limit:
            ConcurrencyLimitSetter.set_concurrency_limit(service_name, new_limit)
            logging.info(f"Concurrency limit lowered for service {service_name}. New limit: {new_limit}")


