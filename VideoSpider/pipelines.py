# -*- coding: utf-8 -*-

import traceback
import pandas as pd
import VideoSpider.items as items
from scrapy.exceptions import DropItem
from VideoSpider.helper.sentence import Sentence
from VideoSpider.helper.trend_content import get_similarity
from VideoSpider.utils import engine_db

engine = engine_db.get_engine(product=True)
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class JudgeMatchPipeline(object):
    """
    判断爬取内容是否和关键字匹配
    """

    def __init__(self, crawler):
        self.is_judge = crawler.settings.get("IS_JUDGE", True)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):

        if not self.is_judge:
            return item

        # 简单判断, 0- 不匹配,1- 模糊匹配,2-精确匹配
        def _key_match(key, x):

            if key in x:
                return 2

            for ch in key:
                if ch not in x:
                    return 0
            return 1

        item['is_match'] = 1
        if item.get("keyword"):
            content = "".join(
                [item.get('title', ''), item.get('content', ''), item.get('content_original', '')]
            )
            item['is_match'] = _key_match(item['keyword'], content)
            if not item['is_match']:
                raise DropItem(
                    '{}: Drop item is_match=0! :{}'.format(
                        spider.name, item.get('href', item.get("url", ""))
                    )
                )
        return item


class MySQLStorePipeline(object):
    def process_item(self, item, spider):
        return item
