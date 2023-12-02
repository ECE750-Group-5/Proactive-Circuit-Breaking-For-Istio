import requests
import json



class MetricsQuerier:
    def __init__(self, prometheus_url: str) -> None:
        """
        Initializes a MetricsQuerier object.

        Args:
            service_names (list): List of service names.
            prometheus_url (str): URL of the Prometheus server.
        """
        self.prometheus_url = prometheus_url
    
    def query_metrics(self, query: str) -> float:
        """
        Queries metrics from the Prometheus server.

        Args:
            query (str): Prometheus query string.

        Returns:
            float: Result of the query as a float value.
        """
        try:
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
                float: CPU usage percentage with one decimal, for example, 92.5%.
            """
            query = f'sum(rate(container_cpu_usage_seconds_total{{container_label_name="{service_name}"}}[1m]))/sum(container_spec_cpu_quota{{container_label_name="{service_name}"}}/container_spec_cpu_period{{container_label_name="{service_name}"}}) * 100'
            percentage = self.query_metrics(query)
            return round(percentage, 1)

    
    def query_memory_usage_percentage(self) -> float:
        """
        Queries the memory usage percentage metric.

        Returns:
            float: Memory usage percentage.
        """
        pass

    def query_non_500_rate(self) -> float:
        """
        Queries the non-500 rate metric.

        Returns:
            float: Non-500 rate.
        """
        pass

    def query_p99_latency() -> float:
        """
        Queries the p99 latency metric.

        Returns:
            float: P99 latency.
        """
        pass

if __name__ == "__main__":
    prometheus_url = 'http://localhost:9090/api/v1/query'
    metrics_querier = MetricsQuerier(prometheus_url)
    cpu = metrics_querier.query_cpu_usage_percentage("httpbin")
    print(cpu)