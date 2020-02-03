import time
from functools import wraps

'''
Usage:
At the start you must first instantiate your rate limiter
ex. rateLimitManger = RateLimitManager

Then simply add a rate limit decorator to each API endpoint under the route
ex. 
    @app.route("abc")
    @rateLimitManager.limit(rateNum=7,rateTime=60*15)
    func endpoint():
        ...function body ...

'''
class RateLimit:
    def __init__(self, name = "", rateNum=0,rateTime=0):
        self.name = name
        self.rateNum = rateNum
        self.rateTime = rateTime
        self.requestHistory = []

    def rateLimitCheck(self):
        if self.rateTime > 0 and self.rateNum > 0:
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
    
    #rateNum is the number of requests per some rateTime interval
    #rateTime corresponds to the number of seconds per interval
    #ex. rateNum = 2, rateTime = 60 means 2 requests per second maximum
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

