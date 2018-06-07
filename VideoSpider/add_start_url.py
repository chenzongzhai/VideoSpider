# -*- coding: utf-8 -*-

import time
import redis
import settings
from apscheduler.schedulers.blocking import BlockingScheduler

"""
    scrapy_redis分布式爬取需手动添加start_url 到redis
"""

rd = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PWD
)
start_urls = {
    "VideoSpider:music_qq_spider:start_urls":
        [
            "https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list"
            "&key=all_all_all&pagesize=100&pagenum=1&format=jsonp"
        ],
    "VideoSpider:music_baidu_spider:start_urls":
        [
            "http://music.baidu.com"
        ],
    "VideoSpider:music_163_spider:start_urls":
        [
            "https://music.163.com"
        ],
}


def main():
    for redis_key, urls in start_urls.items():
        for url in urls:
            print("add: {} at {}".format(url, time.strftime("%Y-%m-%d", time.localtime(time.time()))))
            rd.lpush(redis_key, url)


if __name__ == "__main__":
    main()
    # sched = BlockingScheduler()
    # sched.add_job(main, 'cron', hour='5-21/6')
    # sched.start()
