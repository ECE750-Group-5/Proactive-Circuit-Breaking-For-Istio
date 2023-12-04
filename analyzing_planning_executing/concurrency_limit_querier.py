import json
from subprocess import PIPE, run

class ConcurrencyLimitQuerier:
    def __init__(self) -> None:
        pass

    @staticmethod
    def query_concurrency_limit(service_name):
        destination_rule_query = f"kubectl get destinationrule {service_name} -o json"
        destination_rule_json_str = run(destination_rule_query, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout
        destination_rule_json = json.loads(destination_rule_json_str)
        concurrency_limit = destination_rule_json["spec"]["trafficPolicy"]["connectionPool"]["http"]["http1MaxPendingRequests"]
        return int(concurrency_limit)
    
