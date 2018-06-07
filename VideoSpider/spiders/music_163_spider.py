# -*- coding: utf-8 -*-

import re
from scrapy import Request
from VideoSpider.items import MusicItem
from VideoSpider.spiders.base_redis_spider import BaseRedisSpider


class Music163Spider(BaseRedisSpider):
    name = "music_163_spider"
    # start_url = "https://music.163.com"
    # allowed_domains = ["music.163.com"]
    redis_key = 'VideoSpider:{}:start_urls'.format(name)
    source = "网易云音乐"
    source_id = 2
    custom_settings = {
        "DOWNLOAD_DELAY": 5,
        "SCHEDULER_DUPEFILTER_KEY": "VideoSpider:{}:dupefilter".format(name),
        "SCHEDULER_QUEUE_KEY": "VideoSpider:{}:requests".format(name),
    }

    def __init__(self, *args, **kwargs):
        super(Music163Spider, self).__init__(*args, **kwargs)

    # def start_requests(self):
    #
    #     return [Request(
    #         url=self.start_url,
    #         callback=self.parse
    #     )]

    def parse(self, response):
        self.log(response.url)
        urls = response.xpath("//a/@href").extract()
        for url in urls:
            if not isinstance(url, str):
                continue
            url = response.urljoin(url)
            if re.search(r'https?://music\.163\.com/song\?id=\d+$', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse_item,
                    priority=100,
                )
            if re.search(r'https?://music\.163\.com\S*'
                         r'(/artist|/discover|/playlist)($|[^\{]+$)', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse,
                    dont_filter=True,
                )

    def parse_item(self, response):

        # 发布时间
        def _get_pubdate(body):
            m = re.search(r'"pubDate": "(\d{4}-\d{2}-\d{2})T', body, re.S)
            if m:
                pubdate = m.group(1)
                if pubdate != "0000-00-00":
                    return pubdate

        # 歌词
        def _get_song(soup):
            name = soup.xpath('//em[@class="f-ff2"]/text()').extract_first()
            name_cn = soup.xpath('//div[@class="subtit f-fs1 f-ff2"]/text()').extract_first()
            if name_cn and name:
                return name + "({})".format(name_cn)
            elif name:
                return name
            else:
                return ""

        self.log("parse_item:" + response.url)
        div_sel = response.xpath('//div[@class="cnt"]')
        urls = response.xpath("//a/@href").extract()

        for url in urls:
            if not url or type(url) != str:
                continue
            url = response.urljoin(url)
            if re.search(r'https?://music\.163\.com/song\?id=\d+$', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse_item,
                    priority=100,
                )
            elif re.search(r'https?://music\.163\.com\S*'
                           r'(/artist|/discover|/playlist)($|[^\{]+$)', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse,
                    dont_filter=True,
                )

        if div_sel:
            item = MusicItem()
            item['song'] = _get_song(response)
            item['song_id'] = div_sel.xpath('//div[@id="lyric-content"]/@data-song-id').extract_first()
            item['song_url'] = response.url
            item['singer'] = div_sel.xpath("//p[contains(., '歌手')]/span/@title").extract_first()
            item['singer_url'] = response.urljoin(div_sel.xpath("//p[contains(., '歌手')]//a/@href").extract_first())
            item['album'] = div_sel.xpath("//p[contains(., '专辑')]//a/text()").extract_first()
            # item['write_words'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_composition'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_lyric'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            item['pubdate'] = _get_pubdate(response.text)
            item['referer'] = response.request.headers.get('Referer')
            item['raw_html'] = div_sel.extract_first()
            item['source_id'] = self.source_id
            self.build_other_item_info(item)
            yield item
        else:
            self.log('error for url: {}'.format(response.url))
