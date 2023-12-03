import time

class Plan:
    ACTION_SET_LIMIT = 0
    ACTION_RAISE_LIMIT = 1
    ACTION_LOWER_LIMIT = 2
    def __init__(self, action, new_limit):
        self.action = action
        self.new_limit = new_limit
        self.timestamp = time.time()
    
    def get_action(self):
        return self.action
    
    def get_new_limit(self):
        return self.new_limit
    
    def get_timestamp(self):
        return self.timestamp