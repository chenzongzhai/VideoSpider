# -*- encoding: utf-8 -*-

import logging
from w3lib.url import safe_url_string
from scrapy.exceptions import IgnoreRequest
from scrapy.utils.response import get_meta_refresh
from scrapy.downloadermiddlewares.redirect import BaseRedirectMiddleware

logger = logging.getLogger(__name__)

off_keys = ["404.html"]


# 清除 Referer
class PanSoMiddleware(BaseRedirectMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):

        if request.meta.get("local_redirect"):
            location_url = ""
            # logger.debug("local redirect middlewares: {}".format(response.url))
            if response.status == 302:
                location_url = safe_url_string(response.headers.get("location", ""))

            for off_key in off_keys:
                if off_key in location_url:
                    # response.status = 200
                    # request.meta["is_404"] = True
                    # ignore the page
                    # request.meta["dont_redirect"] = True
                    raise IgnoreRequest

            if location_url.startswith("http"):
                reason = "local pan middlewares, redirected!!!"
                request.headers.pop("Referer", None)
                request.priority += 100
                redirected = request.replace(url=location_url)
                return self._redirect(redirected, request, spider, reason) or response

        return response


# meta 重定向
class Pan007Middleware(BaseRedirectMiddleware):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_response(self, request, response, spider):

        if request.meta.get("meta_refresh"):
            # logger.debug("local meta redirect middlewares: {}".format(response.url))
            _, location_url = get_meta_refresh(response)

            if not location_url:
                raise IgnoreRequest

            for off_key in off_keys:
                if off_key in location_url:
                    # ignore the page
                    raise IgnoreRequest

            if location_url.startswith("http"):
                reason = "local pan middlewares, meta redirected!!!"
                request.meta["meta_refresh"] = False
                request.headers.pop('Content-Type', None)
                request.headers.pop("Referer", None)
                request.headers.pop('Content-Length', None)
                request.priority += 100
                redirected = request.replace(url=location_url)
                return self._redirect(redirected, request, spider, reason) or response

        return response
