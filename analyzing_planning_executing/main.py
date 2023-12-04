import logging
from threading import Thread
from analyzer import Analyzer
from metrics_querier import MetricsQuerier
from executor import Executor
from concurrency_limit_setter import ConcurrencyLimitSetter
from event import EventFactory

def add_circuit_breaking(service_name):
    ConcurrencyLimitSetter. set_concurrency_limit(service_name, 100)

def main():
    logging.info("Starting the system.")
    add_circuit_breaking("httpbin")
    prometheus_url = "http://localhost:9090/api/v1/query"
    event_factory = EventFactory()
    analyzer = Analyzer(event_factory)
    analyzer.add_service_to_analyze("httpbin")
    
    plan_queue = analyzer.get_plan_queue()
    executor = Executor(plan_queue)
    analyzer_thread = Thread(target=analyzer.analyze)
    analyzer_thread.start()
    executor_thread = Thread(target=executor.execute)
    executor_thread.start()
    
    

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s', datefmt='%s', level=logging.INFO)
    main()