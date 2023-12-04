from typing import List
import requests
import logging


class MetricsQuerier:
    """
    A class for querying metrics from a Prometheus server.

    Attributes:
        CPU_USAGE_PERCENTAGE (str): Constant for CPU usage percentage metric.
        MEMORY_USAGE_PERCENTAGE (str): Constant for memory usage percentage metric.
        NON_500_PERCENTAGE (str): Constant for non-500 rate metric.
        P99_LATENCY_SECONDS (str): Constant for p99 latency metric.

    Methods:
        __init__(prometheus_url: str): Initializes a MetricsQuerier object.
        _query_metrics(query: str) -> float: Queries metrics from the Prometheus server.
        query_cpu_usage_percentage(service_name: str) -> float: Queries the CPU usage percentage metric.
        query_memory_usage_percentage(service_name: str) -> float: Queries the memory usage percentage metric.
        query_non_500_percentage(service_name: str) -> float: Queries the non-500 rate metric.
        query_p99_latency_seconds(service_name) -> float: Queries the p99 latency metric.
        query_metrics(service_name: str) -> List[float]: Queries all metrics for a given service.
    """

    CPU_USAGE_PERCENTAGE = 'cpu_usage_percentage'
    MEMORY_USAGE_PERCENTAGE = 'memory_usage_percentage'
    NON_500_NON_0_LATENCY = 'non_500_non_0_latency'
    NON_500_NON_0_ARRIVAL_RATE = 'non_500_non_0_arrival_rate'
    PROMETHEUS_URL = 'http://localhost:9090/api/v1/query'

    def __init__(self) -> None:
        pass
    
    @staticmethod
    def _query_metrics(query: str) -> float:
        """
        Queries metrics from the Prometheus server.

        Args:
            query (str): Prometheus query string.

        Returns:
            float: Result of the query as a float value.
        """
        try:
            logging.debug(f"Querying {query}")
            response = requests.get(MetricsQuerier.PROMETHEUS_URL, params={'query': query})
            response.raise_for_status()  # This will raise an exception for HTTP errors
            logging.debug(f"Response: {response.json()}")
            data = response.json()["data"]["result"][0]
            return float(data["value"][1])
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print ("Oops: Something Else", err)
    
    @staticmethod
    def query_cpu_usage_percentage(service_name: str) -> float:
        """
        Queries the CPU usage percentage metric.

        Args:
            service_name (str): The name of the service.

        Returns:
            float: CPU usage percentage in [0, 1].
        """
        query = f'sum(rate(container_cpu_usage_seconds_total{{container_label_name="{service_name}"}}[1m]))/sum(container_spec_cpu_quota{{container_label_name="{service_name}"}}/container_spec_cpu_period{{container_label_name="{service_name}"}})'
        return MetricsQuerier._query_metrics(query)
            

    
    @staticmethod
    def query_memory_usage_percentage(service_name: str) -> float:
        """
        Queries the memory usage percentage metric.

        Args:
            service_name (str): The name of the service.

        Returns:
            float: Memory usage percentage in [0, 1].
        """
        query = f'sum(container_memory_usage_bytes{{container_label_name="{service_name}"}}) / sum(container_spec_memory_limit_bytes{{container_label_name="{service_name}"}})'
        return MetricsQuerier._query_metrics(query)


    @staticmethod
    def query_average_non_500_non_0_latency_seconds(service_name) -> float:
        """
        Queries the average latency metric.

        Args:
            service_name (str): The name of the service.

        Returns:
            float: Average latency in seconds.
        """
        query = f'sum(irate(istio_request_duration_milliseconds_sum{{connection_security_policy="mutual_tls", reporter="destination", response_codes!~"0|5.*", destination_service_name="{service_name}"}}[1m])) / sum(irate(istio_request_duration_milliseconds_count{{connection_security_policy="mutual_tls", reporter="destination", response_codes!~"0|5.*",destination_service_name="{service_name}"}}[1m])) / 1000'
        try:
            return MetricsQuerier._query_metrics(query)
        except Exception as e:
            return 0
    
    @staticmethod
    def query_average_non_500_non_0_arrival_rate(service_name) -> float:
        """
        Queries the average arrival rate metric.

        Args:
            service_name (str): The name of the service.

        Returns:
            float: Average arrival rate in requests per second.
        """
        query = f'round(sum(irate(istio_requests_total{{response_code!~"0|5.*", connection_security_policy="mutual_tls",reporter="destination",destination_service_name=~"{service_name}"}}[5m])), 0.001)'
        try:
            return MetricsQuerier._query_metrics(query)
        except Exception as e:
            return 0
    
    @staticmethod
    def query_cpu_and_memory_usage_percentage(service_name: str) -> List[float]:
        """
        Queries all metrics for a given service.

        Args:
            service_name (str): The name of the service.

        Returns:
            List[float]: List of float values representing the metrics.
        """
        cpu_usage_percentage = MetricsQuerier.query_cpu_usage_percentage(service_name)
        memory_usage_percentage = MetricsQuerier.query_memory_usage_percentage(service_name)
        return [cpu_usage_percentage, memory_usage_percentage]
    

if __name__ == "__main__":
    prometheus_url = 'http://localhost:9090/api/v1/query'
    print(MetricsQuerier.query_average_non_500_non_0_arrival_rate('httpbin'))