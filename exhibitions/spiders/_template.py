import datetime

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class _SPIDER_NAME_(BaseSpider):
    name = "_SPIDER_NAME_"

    EXHIBITION_DATE = "_SHOW_DATE_"
    EXHIBITION_NAME = "_SHOW_NAME_"
    EXHIBITION_WEBSITE = "_SHOW_WEBSITE_"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://example.com",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        # replace with method fetching exhibitors list
        pass

    def parse_exhibitors(self, response: Response):
        # replace with method parse exhibitors data
        pass
