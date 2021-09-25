import datetime

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class TemplateSpider(BaseSpider):
    name = "TemplateSpider"

    EXHIBITION_DATE = datetime.date(1970, 1, 1)
    EXHIBITION_NAME = "Template"
    EXHIBITION_WEBSITE = "https://www.template.com/"

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
