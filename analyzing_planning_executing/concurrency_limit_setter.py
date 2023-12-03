import subprocess


class ConcurrencyLimitSetter:
    def __init__(self):
        pass

    @staticmethod
    def set_concurrency_limit(service_name, concurrency_limit):
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
        """
        command = ["kubectl", "apply", "-f", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        process.communicate(yaml.encode())


if __name__ == "__main__":
    ConcurrencyLimitSetter.set_concurrency_limit("httpbin", 100)