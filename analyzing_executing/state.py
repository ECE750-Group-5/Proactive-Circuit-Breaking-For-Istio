class State:
    def __init__(self) -> None:
        pass


class OverloadingAvoidance(State):
    def __init__(self) -> None:
        pass

    def lower_limit():
        # executor
        pass

    def process(self, event):
        if event.data["cpu_usage_percentage"] >= 90:
            self.lower_limit() # cost time put it in processing thread
        
        # query metrics: cost time, put it in processing thread
        # send new event to queue