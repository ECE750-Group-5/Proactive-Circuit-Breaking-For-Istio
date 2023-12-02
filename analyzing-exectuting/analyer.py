# Implement the loop with queues

# TODO: START + executor + overloading (gabriel)
# aggresive probing


import queue








    def process(self, event):
        
        if event.data["cpu_usage_percentage"] >= 90:
            self.lower_limit() # cost time put it in processing thread
        
        # query metrics: cost time, put it in processing thread
        # send new event to queue



class Analyzer:
    def __init__(self) -> None:
        # priotize new event 
        event_queue = Queue()
        

    def analyze(self) -> None:
        while True:
            try:
                event = self.event_queue.get_nowait()
                self.process_event(event)
            except queue.Empty:
                pass
    
    def process_event(self, event: Event) -> None:
        if event.current_state == Event.START:
            if event.data["cpu_usage_percentage"] >= 90:
               new_event = event(event.OVERLOADING_AVOIDANCE, event.data)
               self.event_queue.put(new_event)
            if event.current_state == Event.OVERLOADING_AVOIDANCE:
                t1 = threading.Thread(target=OverloadingAvoidance.process, args=(event,))
                t1.start()

                    
                