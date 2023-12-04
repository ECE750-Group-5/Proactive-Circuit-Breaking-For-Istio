import subprocess
import logging


class ConcurrencyLimitSetter:
    def __init__(self):
        pass

    @staticmethod
    def set_concurrency_limit(service_name, concurrency_limit):
        if concurrency_limit >= 2**30:
            return
        yaml = f"""
        apiVersion: networking.istio.io/v1alpha3
        kind: DestinationRule
        metadata:
          name: {service_name}
        spec:
          host: {service_name}
          trafficPolicy:
            connectionPool:
              tcp:
                maxConnections: {concurrency_limit}
              http:
                http1MaxPendingRequests: {concurrency_limit}
                http2MaxRequests: {concurrency_limit}
            outlierDetection:
              consecutive5xxErrors: 1
              interval: 1s
              baseEjectionTime: 3m
              maxEjectionPercent: 100
        """
        command = ["kubectl", "apply", "-f", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        process.communicate(yaml.encode())
        logging.info(f"Concurrency limit set for service {service_name}: {concurrency_limit}")
        process.wait()
        


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  ConcurrencyLimitSetter.set_concurrency_limit("httpbin", 100)
