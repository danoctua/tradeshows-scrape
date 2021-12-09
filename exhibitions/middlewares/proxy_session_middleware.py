from scrapy import Request, Spider

from exhibitions.middlewares.proxy_middleware import (
    ProxyDownloaderMiddleware,
    SPIDER_PROXY_CONFIGURATION_ATTRIBUTE,
)
from exhibitions.utils.proxy import get_zyte_session


class ProxySessionDownloaderMiddleware(ProxyDownloaderMiddleware):
    """Middleware for setting proxy with session.

    To use it, be sure to add this to the downloader middlewares in the spider settings
    and set SPIDER_PROXY_CONFIGURATION_ATTRIBUTE attribute for the spider class with proxy configuration
    """

    def process_request(self, request: Request, spider: Spider) -> None:
        proxy_configuration = getattr(spider, SPIDER_PROXY_CONFIGURATION_ATTRIBUTE, {})
        get_zyte_session(request, proxy_configuration)
        return super().process_request(request, spider)
