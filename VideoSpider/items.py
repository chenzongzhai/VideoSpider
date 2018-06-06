# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# 视频类
class VideoItem(scrapy.Item):
    # define the fields for your item here like:
    uuid = scrapy.Field()
    title = scrapy.Field()
    href = scrapy.Field()
    duration = scrapy.Field()
    source = scrapy.Field()
    keyword = scrapy.Field()
    site_name = scrapy.Field()
    is_match = scrapy.Field()
    created_at = scrapy.Field()
    created_by = scrapy.Field()
    referer = scrapy.Field()

    def __str__(self):
        values = ''
        for key, val in self.items():
            values += "{}:{}, \n".format(key, val)
        return values


# 音乐类
class MusicItem(scrapy.Item):
    uuid = scrapy.Field()
    song = scrapy.Field()
    platform = scrapy.Field()
    song_id = scrapy.Field()
    song_url = scrapy.Field()
    singer = scrapy.Field()
    singer_url = scrapy.Field()
    album = scrapy.Field()
    write_words = scrapy.Field()
    song_composition = scrapy.Field()
    content = scrapy.Field()
    pubdate = scrapy.Field()
    source = scrapy.Field()
    source_id = scrapy.Field()
    raw_html = scrapy.Field()
    created_at = scrapy.Field()
    referer = scrapy.Field()
    is_match = scrapy.Field()

    def __str__(self):
        values = ''
        for key, val in self.items():
            if key in ['uuid', 'song', 'singer', 'source']:
                values += "{}:{}, \n".format(key, val)
        return values


# 网盘类
class WangPanItem(scrapy.Item):

    uuid = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    is_match = scrapy.Field()
    share_date = scrapy.Field()
    created_at = scrapy.Field()
    referer = scrapy.Field()
    keyword = scrapy.Field()

    def __str__(self):
        values = ''
        for key, val in self.items():
            values += "{}:{}, \n".format(key, val)
        return values


# 新闻类
class TextItem(scrapy.Item):
    uuid = scrapy.Field()
    title = scrapy.Field()
    href = scrapy.Field()
    content = scrapy.Field()
    source_title = scrapy.Field()
    source_content = scrapy.Field()
    source_url = scrapy.Field()
    source = scrapy.Field()
    is_match = scrapy.Field()
    created_at = scrapy.Field()
    created_by = scrapy.Field()
    keyword = scrapy.Field()

    def __str__(self):
        values = ''
        for key, val in self.items():
            if key in ['uuid', 'title', 'pubdate', 'url']:
                values += "{}:{}, \n".format(key, val)
        return values
