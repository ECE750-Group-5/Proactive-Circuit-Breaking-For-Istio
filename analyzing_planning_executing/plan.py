import time

class Plan:
    ACTION_SET_LIMIT = 0
    ACTION_RAISE_LIMIT = 1
    ACTION_LOWER_LIMIT = 2
    def __init__(self, service_name, action, old_limit, new_limit):
        self.action = action
        self.service_name = service_name
        self.old_limit = old_limit
        self.new_limit = new_limit
        self.timestamp = time.time()
    
    def get_action(self):
        return self.action
    
    def get_new_limit(self):
        return self.new_limit
    
    def get_timestamp(self):
        return self.timestamp
    
    def get_old_limit(self):
        return self.old_limit
    
    def get_service_name(self):
        return self.service_name
    
    def __str__(self) -> str:
        return f"Plan(action={self.action}, service_name={self.service_name}, old_limit={self.old_limit}, new_limit={self.new_limit}, timestamp={self.timestamp})"