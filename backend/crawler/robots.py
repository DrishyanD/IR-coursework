from urllib import robotparser
from urllib.parse import urljoin
import requests

class RobotsChecker:
    def __init__(self, base_url, user_agent, timeout=15):
        self.user_agent = user_agent
        self.timeout = timeout
        self.robots_url = urljoin(base_url, "/robots.txt")
        self.parser = robotparser.RobotFileParser()
        self.loaded = False

    def load(self):
        try:
            response = requests.get(
                self.robots_url,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout,
            )
            response.raise_for_status()
            self.parser.set_url(self.robots_url)
            self.parser.parse(response.text.splitlines())
            self.loaded = True
            return True
        except requests.RequestException:
            self.loaded = False
            return False

    def can_fetch(self, url):
        return self.loaded and self.parser.can_fetch(self.user_agent, url)

    def crawl_delay(self):
        return self.parser.crawl_delay(self.user_agent) if self.loaded else None
