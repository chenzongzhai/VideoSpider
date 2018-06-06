# -*- coding: utf-8 -*-

import hashlib
import VideoSpider.items as items
from scrapy_redis.spiders import RedisSpider
from VideoSpider.helper.task_item import TaskItem
from VideoSpider.utils.data_convert import get_now_time


class BaseRedisSpider(RedisSpider):

    redis_url = 'redis://:AAaa1115@58.87.101.142:6379/4'

    def __init__(self, *args, **kwargs):
        super(BaseRedisSpider, self).__init__(*args, **kwargs)

    @classmethod
    def update_settings(cls, settings):
        redis_settings = {
            "REDIS_URL": None,
            "SCHEDULER": "scrapy_redis.scheduler.Scheduler",
            "DUPEFILTER_CLASS": "scrapy_redis.dupefilter.RFPDupeFilter",
            # 允许暂停，redis请求记录不丢失
            "SCHEDULER_PERSIST": True,
            # 默认的scrapy-redis请求队列形式（按优先级）
            "SCHEDULER_QUEUE_CLASS": "scrapy_redis.queue.SpiderPriorityQueue",
            # redis中start url数据类型为set时设置此项为True，默认为False
            # "REDIS_START_URLS_AS_SET": True,
            # "ITEM_PIPELINES": {
            #     'scrapy_redis.pipelines.RedisPipeline': 300,
            # }
        }
        # 子类的配置可以覆盖redis_settings
        # redis_url必须配置custom_settings或类变量中
        if cls.custom_settings is not None:
            cls.custom_settings = dict(redis_settings, **cls.custom_settings)
        else:
            cls.custom_settings = redis_settings
        if cls.redis_url is not None:
            cls.custom_settings["REDIS_URL"] = cls.redis_url
        settings.setdict(cls.custom_settings or {}, priority='spider')

    def build_other_item_info(self, item):
        url = item.get("url", item.get("song_url", item.get("href", "")))
        item['created_at'] = get_now_time()
        item['uuid'] = hashlib.md5(url.encode('utf8')).hexdigest()
