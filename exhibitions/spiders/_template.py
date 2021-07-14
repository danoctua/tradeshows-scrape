import datetime

from scrapy.http import Response

from exhibitions.spiders.base_spider import BaseSpider


class TemplateSpider(BaseSpider):
    name = "TemplateSpider"

    EXHIBITION_DATE = datetime.date(1970, 1, 1)
    EXHIBITION_NAME = "Template"
    EXHIBITION_WEBSITE = "https://www.template.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = None  # create new and replace with class name

    URLS = [
        "https://example.com",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    def fetch_exhibitors(self, response: Response):
        # replace with method fetching exhibitors list
        pass

    def parse_exhibitors(self, response: Response):
        # replace with method parse exhibitors data
        pass
