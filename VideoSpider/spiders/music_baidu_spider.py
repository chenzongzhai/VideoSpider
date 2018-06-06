# -*- coding: utf-8 -*-

import re
from scrapy import Request
from scrapy.selector import Selector
from VideoSpider.items import MusicItem
from VideoSpider.spiders.base_redis_spider import BaseRedisSpider


class MusicBaiduSpider(BaseRedisSpider):
    name = "music_baidu_spider"
    # start_url = "http://music.baidu.com"
    # allowed_domains = ["music.baidu.com"]
    redis_key = 'VideoSpider:{}:start_urls'.format(name)
    source = "百度音乐"
    source_id = 3
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "SCHEDULER_DUPEFILTER_KEY": "VideoSpider:{}:dupefilter".format(name),
        "SCHEDULER_QUEUE_KEY": "VideoSpider:{}:requests".format(name),
    }

    def __init__(self, *args, **kwargs):
        super(MusicBaiduSpider, self).__init__(*args, **kwargs)

    # 总页数
    def _page_navigator(self, page_nav):
        page, size = 0, 0
        mt = re.search("'total'\s?:\s?(\d+),\s?'size'\s?:\s?(\d+),", page_nav, re.S)
        if mt and len(mt.groups()) == 2:
            total = int(mt.group(1))
            size = int(mt.group(2))
            if total > size:
                page = total // size
        self.log('parse num page {}, size {}'.format(page, size))
        return page, size

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
            if not url or type(url) != str:
                continue
            url = response.urljoin(url)
            if re.search(r'https?://music\.baidu\.com/song/(s/)?\w+$', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse_item,
                    priority=100,
                )
            elif re.search(r'https?://music\.baidu\.com'
                           r'(/tag|/artist|/songlist|/album|/top)\S*', url, re.S):
                yield Request(
                    url=url.split('?pst')[0],
                    callback=self.parse,
                    dont_filter=True,
                )

        next_tags = response.xpath(
            '//div[contains(@class, "page-navigator-hook page-navigator")]'
        )
        ting_uid = response.xpath('//div[@id="baseInfo"]/@ting_uid').extract_first()
        for tag in next_tags:
            next_a = tag.xpath('.//a[contains(., "下一页")]/@href').extract_first()
            if next_a:
                if 'getalbum' in next_a.lower() or 'getsong' in next_a.lower():
                    page_nav = tag.xpath('@class').extract_first()
                    page, size = self._page_navigator(page_nav)
                    if ting_uid and page:
                        next_api = next_a.replace(
                            'artist/getSong', 'user/getsongs'
                        ).replace(
                            'artist/getAlbum', 'user/getalbums'
                        ).strip()
                        for num in range(1, page+1):
                            nav = '?start={}&ting_uid={}'.format(num * size, ting_uid)
                            next_page = response.urljoin(
                                next_api.split('?')[0] + nav
                            )
                            yield Request(
                                url=next_page,
                                callback=self.parse_json,
                                priority=page-num+100,
                                dont_filter=True,
                            )

    # page为json形式
    def parse_json(self, response):
        self.log(response.url)
        body = response.text
        songs_comp = re.compile(r'href=\\"(\\/song(\\/s)?\\/\w+\\)"', re.S)
        albums_comp = re.compile(r'href=\\"(\\/album\\/\d+\\)"', re.S)
        song_list = re.findall(songs_comp, body)
        album_list = re.findall(albums_comp, body)
        for song in song_list:
            if song:
                song_url = 'http://music.baidu.com' + song[0].replace('\\', '')
                yield Request(
                    url=song_url,
                    callback=self.parse_item,
                    priority=100,
                )

        for album in album_list:
            if album:
                album_url = 'http://music.baidu.com' + album.replace('\\', '')
                yield Request(
                    url=album_url,
                    callback=self.parse,
                    priority=50,
                    dont_filter=True,
                )

    def parse_item(self, response):

        def _get_pubdate(body, song_id):
            m = re.search(r"data-btndata='.*?" + song_id + ".*?(\d{4}-\d{2}-\d{2}).*?'", body, re.S)
            if m:
                pubdate = m.group(1)
                if pubdate != "0000-00-00":
                    return pubdate

        self.log("parse_item:" + response.url)
        # 命令行调试代码
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        div_sel = response.xpath('//div[@class="song-info-box fl"]')
        urls = response.xpath("//a/@href").extract()

        for url in urls:
            if not url or type(url) != str:
                continue
            url = response.urljoin(url)
            if re.search(r'https?://music\.baidu\.com/song/(s/)?\w+$', url, re.S):
                yield Request(
                    url=url,
                    callback=self.parse_item,
                    priority=100,
                )
            elif re.search(r'https?://music\.baidu\.com'
                           r'(/tag|/artist|/songlist|/album|/top)\S*', url, re.S):
                yield Request(
                    url=url.split('?pst')[0],
                    callback=self.parse,
                    dont_filter=True,
                )

        if div_sel:
            url = response.url
            item = MusicItem()
            item['song'] = div_sel.xpath('//span[@class="name"]/text()').extract_first()
            item['platform'] = div_sel.xpath('//span[@class="songpage-version"]/text()').extract_first()
            item['song_id'] = url.split('/')[-1]
            item['song_url'] = url
            item['singer'] = div_sel.xpath('//span[@class="author_list"]/@title').extract_first()
            item['singer_url'] = response.urljoin(
                div_sel.xpath('//li[contains(., "歌手")]/span[@class="author_list"]/a/@href').extract_first()
            )
            album = div_sel.xpath("//li[contains(., '专辑')]/a/text()").extract_first()
            item['album'] = album.strip() if album else None
            # item['write_words'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_composition'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_lyric'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            item['pubdate'] = _get_pubdate(response.text, item['song_id'])
            item['referer'] = response.request.headers.get('Referer')
            item['raw_html'] = div_sel.extract_first()
            item['source_id'] = self.source_id
            item['source'] = self.source
            self.build_other_item_info(item)
            yield item
        else:
            self.log('error for url: {}'.format(response.url))
