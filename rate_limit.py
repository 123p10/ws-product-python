import time
from functools import wraps
class RateLimit:
    def __init__(self, name = "", rateNum=0,rateTime=0):
        self.name = name
        self.rateNum = rateNum
        self.rateTime = rateTime
        self.requestHistory = []
    def rateLimitCheck(self):
        if self.rateTime != -1 and self.rateNum != -1:
            rateFlag = False
            currTime = int(time.time())
            #clear stack
            while len(self.requestHistory) > 0  and currTime - self.requestHistory[0] > self.rateTime:
                self.requestHistory.pop(0)
            if len(self.requestHistory) < self.rateNum:
                rateFlag = True
                self.requestHistory.append(currTime)
            return rateFlag
        return True
        
class RateLimitManager:
    def __init__(self):
        self.rateLimits = {}
    #rateNum is the number of requests per some rateTime
    #rateTime corresponds to the number of seconds interval
    def limit(self,rateNum, rateTime):
        def wrap(f):
            def wrapped_f(*args):
                calling_name = f.__name__
                print(calling_name)
                if calling_name not in self.rateLimits:
                    self.addLimit(calling_name,rateNum,rateTime)
                if self.rateLimits.get(calling_name).rateLimitCheck():
                    return f(*args)
                else:
                    return "You are doing that too often"
            wrapped_f.__name__ = f.__name__ + "__rate__wrapper"
            return wrapped_f
        return wrap
    def addLimit(self,name,rateNum, rateTime):
        self.rateLimits[name] = RateLimit(name,rateNum,rateTime)

