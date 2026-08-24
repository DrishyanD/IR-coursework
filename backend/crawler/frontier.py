from collections import deque

class URLFrontier:
    def __init__(self):
        self.queue = deque()
        self.queued = set()
        self.visited = set()

    def add(self, url):
        if url in self.queued or url in self.visited:
            return False
        self.queue.append(url)
        self.queued.add(url)
        return True

    def next(self):
        if not self.queue:
            return None
        url = self.queue.popleft()
        self.queued.discard(url)
        return url

    def mark_visited(self, url):
        self.visited.add(url)

    def __len__(self):
        return len(self.queue)
