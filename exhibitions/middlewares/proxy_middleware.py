from scrapy import Request, Spider

from exhibitions.utils.proxy import set_proxy


SPIDER_PROXY_ATTRIBUTE = "PROXY"


class ProxyDownloaderMiddleware:
    """Middleware for setting proxy.

    To use it, be sure to add this to the downloader middlewares in the spider settings
    and set SPIDER_PROXY_CONFIGURATION_ATTRIBUTE attribute for the spider class with proxy configuration
    """

    @staticmethod
    def process_request(request: Request, spider: Spider) -> None:
        proxy_configuration = getattr(spider, SPIDER_PROXY_ATTRIBUTE)
        set_proxy(request, proxy_configuration)
