# -*- coding: utf-8 -*-

import re
import json
import hashlib
import requests
from scrapy import Request
from scrapy.selector import Selector
from VideoSpider.helper.check_url_in import check_uuid
from VideoSpider.items import MusicItem
from VideoSpider.spiders.base_redis_spider import BaseRedisSpider

"""
请求数据均为json, 抓包分析
"""


class MusicQQSpider(BaseRedisSpider):
    name = "music_qq_spider"
    # start_url = "https://y.qq.com/"
    redis_key = 'VideoSpider:{}:start_urls'.format(name)
    source = "QQ音乐"
    source_id = 1
    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "SCHEDULER_DUPEFILTER_KEY": "VideoSpider:{}:dupefilter".format(name),
        "SCHEDULER_QUEUE_KEY": "VideoSpider:{}:requests".format(name),
    }

    def __init__(self, scrapy_task_id=None, *args, **kwargs):
        super(MusicQQSpider, self).__init__(scrapy_task_id, *args, **kwargs)
        self.singer_list = 'https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer' \
                           '&page=list&key=all_all_all&pagesize=100&pagenum={}&format=jsonp'
        self.song_list = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_track_cp.fcg?' \
                         'singermid={}&num={}&begin={}'
        self.song_url = 'https://y.qq.com/n/yqq/song/{}.html'
        self.album_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?' \
                         'albummid={}&format=jsonp'
        self.desc_url = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric.fcg?nobase64=1&' \
                        'musicid={}&format=jsonp&inCharset=utf8&outCharset=utf-8'
        self.requests_json_header = {
            'Host': 'c.y.qq.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
        }

    def _check_json(self, body, url):
        req_dict = json.loads(body)
        if req_dict.get('message', '') != "succ":
            self.log('error for {}'.format(url))
        return req_dict.get('data', {})

    def parse(self, response):
        url = response.url
        self.log(url)
        res_json = self._check_json(response.text, url)
        for singer in res_json.get('list', []):
            mid = singer.get('Fsinger_mid')
            if mid:
                song_list_url = self.song_list.format(mid, 1000, 0)
                yield Request(
                    url=song_list_url,
                    callback=self.parse_song_list,
                    meta={
                        "singer_mid": mid,
                        "begin": 1000,
                    },
                    headers={
                        "Referer": "https://y.qq.com/n/yqq/singer/{}.html".format(mid),
                    },
                    priority=50,
                    # dont_filter=True,
                )

        if 'pagenum=1&' in url:
            total_page = res_json.get('total_page', 2)
            for page in range(2, total_page):
                url = self.singer_list.format(page)
                yield Request(
                    url=url,
                    callback=self.parse,
                    headers={
                        "Referer": "https://y.qq.com/portal/singer_list.html",
                    },
                    priority=-page,
                    # dont_filter=True,
                )

    def parse_song_list(self, response):
        url = response.url
        self.log(url)
        mid = response.meta['singer_mid']
        begin = response.meta['begin']
        res_json = self._check_json(response.text, url)
        for song_dict in res_json.get('list', []):
            yield self.song_items(song_dict)

        # 判断是否有下一页
        total_num = res_json.get('total', 0)
        if total_num > begin:
            song_list_url = self.song_list.format(mid, total_num-begin, begin)
            yield Request(
                url=song_list_url,
                callback=self.parse_song_list,
                meta={
                    "singer_mid": mid,
                    "begin": total_num,
                },
                headers={
                    "Referer": "https://y.qq.com/n/yqq/singer/{}.html".format(mid),
                },
                priority=100,
                # dont_filter=True,
            )

    def song_items(self, song_dict):

        def _get_pubdate(albummid):

            if albummid:
                album_url = self.album_url.format(albummid)
                self.log('get pubdate {}'.format(album_url))
                req = requests.get(album_url, headers=self.requests_json_header, timeout=20)
                if req.status_code == 200:
                    content_dict = json.loads(req.text)
                    adate = content_dict.get('data', {}).get('aDate')
                    if adate != '0000-00-00':
                        return adate

        def _get_content(song_id):

            if song_id:
                desc_url = self.desc_url.format(song_id)
                self.log('get lyric {}'.format(desc_url))
                req = requests.get(desc_url, headers=self.requests_json_header, timeout=20)
                if req.status_code == 200:
                    content_html = req.text
                    m = re.search('back\(({.*})\)', content_html, re.S)
                    if m:
                        content_json = m.group(1)
                        content_dict = json.loads(content_json)
                        return content_dict.get('lyric')

        def _get_singer(singer_list):
            singer_name, singer_url = [], None
            if len(singer_list) > 0:
                singer_mid = singer_list[0].get('mid' '')
                if singer_mid:
                    singer_url = "https://y.qq.com/n/yqq/singer/{}.html".format(singer_mid)
            for singer in singer_list:
                singer_name.append(singer.get('name', ''))
            return ' / '.join(singer_name), singer_url

        music_data = song_dict.get('musicData', {})
        songid = music_data.get('songid')
        songmid = music_data.get('songmid')
        if songmid:
            song_url = self.song_url.format(songmid)
            self.requests_json_header.update(
                {
                    "Referer": song_url,
                }
            )
            uuid = hashlib.md5(song_url.encode('utf8')).hexdigest()
            if check_uuid(uuid, self.name):
                self.log('having song {}'.format(song_url))
                return
            item = MusicItem()
            item['song'] = music_data.get('songname')
            # item['platform'] = _get_singer(div_sel.xpath('//div[@class="data__singer"]'))
            item['song_id'] = songid
            item['song_url'] = song_url
            item['singer'], item['singer_url'] = _get_singer(music_data.get('singer', []))
            # item['singer_url'] = response.urljoin()
            item['album'] = music_data.get('albumname')
            # item['write_words'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_composition'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            item['content'] = _get_content(songid)
            item['pubdate'] = _get_pubdate(music_data.get('albummid'))
            # item['referer'] = response.request.headers.get('Referer')
            item['raw_html'] = json.dumps(song_dict)
            item['source_id'] = self.source_id
            self.build_other_item_info(item, self.source)
            return item

    def parse_song(self, response, sid):

        headers = {
            'Host': 'c.y.qq.com',
            'Referer': response.url,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
        }

        def _get_pubdate(body):

            m = re.search(r'"albummid"\s?:\s?"(\w+)"', body, re.S)
            if m:
                album_id = m.group(1)

                if album_id:
                    album_url = self.album_url.format(album_id)
                    self.log('get pubdate {}'.format(album_url))
                    req = requests.get(album_url, headers=headers, timeout=20)
                    if req.status_code == 200:
                        content_dict = json.loads(req.text)
                        adate = content_dict.get('data', {}).get('aDate')
                        if adate != '0000-00-00':
                            return adate

        def _get_content(song_id):

            if song_id:
                desc_url = self.desc_url.format(song_id)
                self.log('get lyric {}'.format(desc_url))
                req = requests.get(desc_url, headers=headers, timeout=20)
                if req.status_code == 200:
                    content_html = req.text
                    m = re.search('back\(({.*})\)', content_html, re.S)
                    if m:
                        content_json = m.group(1)
                        content_dict = json.loads(content_json)
                        return content_dict.get('lyric')

        def _get_singer(soup):
            singer = []
            list_a = soup.xpath("a/@title")
            for a in list_a:
                singer.append(a.extract())
            return ' / '.join(singer)

        self.log("parse_item:" + response.url)
        sel = Selector(response)
        div_sel = sel.xpath('//div[@class="data__cont"]')

        if div_sel:
            url = response.url
            item = MusicItem()
            item['song'] = div_sel.xpath('//h1[@class="data__name_txt"]/@title').extract_first()
            # item['platform'] = _get_singer(div_sel.xpath('//div[@class="data__singer"]'))
            item['song_id'] = sid
            item['song_url'] = url
            item['singer'] = _get_singer(div_sel.xpath('//div[@class="data__singer"]'))
            item['singer_url'] = response.urljoin(
                div_sel.xpath('//div[@class="data__singer"]/a/@href').extract_first()
            )
            album = div_sel.xpath('//li[contains(., "专辑")]/a[@class="js_album"]/@title').extract_first()
            item['album'] = album.strip() if album else None
            # item['write_words'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            # item['song_composition'] = div_sel.xpath('//em[@class="f-ff2"]/text()')
            item['content'] = _get_content(sid)
            item['pubdate'] = _get_pubdate(response.text)
            item['referer'] = response.request.headers.get('Referer')
            item['raw_html'] = div_sel.extract_first()
            item['source_id'] = self.source_id
            self.build_other_item_info(item, self.source)
            yield item
        else:
            self.log('error for url: {}'.format(response.url))
