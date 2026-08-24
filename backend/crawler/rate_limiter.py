import time

class RateLimiter:
    def __init__(self, delay=2.0):
        self.delay = max(0.0, delay)
        self.last_request = 0.0

    def wait(self):
        remaining = self.delay - (time.monotonic() - self.last_request)
        if remaining > 0:
            time.sleep(remaining)
        self.last_request = time.monotonic()
