import datetime

from exhibitions.constants import PROXY_ZYTE
from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class HDExpoSpider(BaseA2ZSpider):
    name = "HDExpoSpider"

    EXHIBITION_DATE = datetime.date(2022, 4, 26)
    EXHIBITION_NAME = "HD Expo"
    EXHIBITION_WEBSITE = "https://hdexpo.hospitalitydesign.com/"

    URLS = [
        "https://hd.a2zinc.net/HDExpo2022/Public/exhibitors.aspx?Index=All",
    ]

    PROXY = PROXY_ZYTE

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "exhibitions.middlewares.proxy_middleware.ProxyDownloaderMiddleware": 0,
        },
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Upgrade-Insecure-Requests": 1,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "hd.a2zinc.net",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-GPC": 1,
    }
