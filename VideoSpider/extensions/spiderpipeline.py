# -*- coding: utf-8 -*-

from scrapy import signals

"""
    爬虫扩展,可记录爬虫运行状态等
"""


class SpiderOpenCloseLogging(object):

    def __init__(self, item_count):
        self.item_count = item_count
        self.items_scraped = 0

    @classmethod
    def from_crawler(cls, crawler):
        # first check if the extension should be enabled and raise
        # NotConfigured otherwise
        # if not crawler.settings.getbool('MYEXT_ENABLED'):
        #     raise NotConfigured

        # get the number of items from settings
        item_count = crawler.settings.getint('MYEXT_ITEMCOUNT', 1000)

        # instantiate the extension object
        ext = cls(item_count)

        # connect the extension object to signals
        crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        # return the extension object
        return ext

    def spider_opened(self, spider):
        spider.log("opened spider %s" % spider.name)

    def spider_closed(self, spider):
        spider.log("closed spider %s" % spider.name)

        stats = spider.crawler.stats
        error_count = stats._stats.get('log_count/ERROR', 0)
        spider.log('error_count:{}'.format(error_count))

    def item_scraped(self, item, spider):
        pass
        # self.items_scraped += 1
        # if self.items_scraped % self.item_count == 0:
        #     spider.log("scraped %d items" % self.items_scraped)
