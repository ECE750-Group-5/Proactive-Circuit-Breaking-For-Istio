from typing import List
import requests
import json



class MetricsQuerier:
    CPU_USAGE_PERCENTAGE = 'cpu_usage_percentage'
    MEMORY_USAGE_PERCENTAGE = 'memory_usage_percentage'
    NON_500_PERCENTAGE = 'non_500_percentage'
    P99_LATENCY_SECONDS = 'p99_latency_seconds'
    def __init__(self, prometheus_url: str) -> None:
        """
        Initializes a MetricsQuerier object.

        Args:
            service_names (list): List of service names.
            prometheus_url (str): URL of the Prometheus server.
        """
        self.prometheus_url = prometheus_url
    
    def _query_metrics(self, query: str) -> float:
        """
        Queries metrics from the Prometheus server.

        Args:
            query (str): Prometheus query string.

        Returns:
            float: Result of the query as a float value.
        """
        try:
            print(query)
            response = requests.get(self.prometheus_url, params={'query': query})
            response.raise_for_status()  # This will raise an exception for HTTP errors
            print(response.json())
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

    def query_cpu_usage_percentage(self, service_name: str) -> float:
            """
            Queries the CPU usage percentage metric.

            Args:
                service_name str: The name of the service.

            Returns:
                float: CPU usage percentage in [0, 1].
            """
            query = f'sum(rate(container_cpu_usage_seconds_total{{container_label_name="{service_name}"}}[1m]))/sum(container_spec_cpu_quota{{container_label_name="{service_name}"}}/container_spec_cpu_period{{container_label_name="{service_name}"}})'
            return self._query_metrics(query)
            

    
    def query_memory_usage_percentage(self, service_name: str) -> float:
        """
        Queries the memory usage percentage metric.

        Returns:
            float: Memory usage percentage in [0, 1].
        """
        query = f'sum(container_memory_usage_bytes{{container_label_name="{service_name}"}}) / sum(container_spec_memory_limit_bytes{{container_label_name="{service_name}"}})'
        return self._query_metrics(query)


    def query_non_500_percentage(self, service_name: str) -> float:
        """
        Queries the non-500 rate metric.

        Args:
            service_name (str): The name of the service.

        Returns:
            float: Non-500 percentage, with one decimal, for example, 92.5%.
        """
        query = f'sum(irate(istio_requests_total{{connection_security_policy="mutual_tls", reporter="destination", destination_service_name="{service_name}", response_code!~"5.*"}}[1m])) / sum(irate(istio_requests_total{{connection_security_policy="mutual_tls", reporter="destination", destination_service_name="{service_name}"}}[1m]))'
        return self._query_metrics(query)
        return percentage

    def query_p99_latency_seconds(self, service_name) -> float:
        """
        Queries the p99 latency metric.

        Returns:
            float: P99 latency in ms.
        """
        query = f'histogram_quantile(0.99, sum(irate(istio_request_duration_milliseconds_bucket{{connection_security_policy="mutual_tls", reporter="destination", destination_service_name="{service_name}"}}[1m])) by (le)) / 1000'
        return self._query_metrics(query)
    
    def query_metrics(self, service_name: str) -> List[float]:
        """
        Queries all metrics for a given service.

        Args:
            service_name (str): The name of the service.

        Returns:
            List[float]: List of float values representing the metrics.
        """
        cpu_usage_percentage = self.query_cpu_usage_percentage(service_name)
        memory_usage_percentage = self.query_memory_usage_percentage(service_name)
        non_500_percentage = self.query_non_500_percentage(service_name)
        p99_latency_seconds = self.query_p99_latency_seconds(service_name)
        return [cpu_usage_percentage, memory_usage_percentage, non_500_percentage, p99_latency_seconds]

if __name__ == "__main__":
    prometheus_url = 'http://localhost:9090/api/v1/query'
    metrics_querier = MetricsQuerier(prometheus_url)
    print(metrics_querier.query_metrics('httpbin'))