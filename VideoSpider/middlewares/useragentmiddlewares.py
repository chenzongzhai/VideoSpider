# -*- encoding: utf-8 -*-

import random
import logging
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

logger = logging.getLogger(__name__)


class RotateUserAgentMiddleware(UserAgentMiddleware):
    """避免被ban策略之一：使用useragent池。
    使用注意：需在settings.py中进行相应的设置。
    """
    def __init__(self, settings):
        super(RotateUserAgentMiddleware, self).__init__()
        self.user_agents = settings.get("USER_AGENTS")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        if not request.headers.get("User-Agent"):
            ua = random.choice(self.user_agents)
            if ua:
                logger.debug('Current UserAgent: ' + ua)
                request.headers.setdefault('User-Agent', ua)
