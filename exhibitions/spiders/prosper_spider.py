import datetime

from exhibitions.constants import PROXY_ZYTE
from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class ProsperSpider(BaseA2ZSpider):
    name = "ProsperSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 14)
    EXHIBITION_NAME = "Prosper 2022"
    EXHIBITION_WEBSITE = "https://prospershow.com/"

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
        "DOWNLOADER_MIDDLEWARES": {
            "exhibitions.middlewares.proxy_middleware.ProxyDownloaderMiddleware": 0,
        },
    }

    PROXY = PROXY_ZYTE

    URLS = [
        "https://prosper.a2zinc.net/Prosper2021/Public/exhibitors.aspx?Index=All",
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Upgrade-Insecure-Requests": 1,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "prosper.a2zinc.net",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-GPC": 1,
    }
