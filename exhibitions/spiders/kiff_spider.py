import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class KiffSpider(BaseSpider):
    name = "KiffSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 2)
    EXHIBITION_NAME = "Kiff - Kiev International Furniture Forum"
    EXHIBITION_WEBSITE = "https://www.kiff.kiev.ua/en/home-eng/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.kiff.kiev.ua/en/exhibitors-list-of-kiff-2021/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath("//table//tr/td/text()").getall()
        for exhibitor_name in exhibitors:
            exhibitor_item = self.item_loader(item=self.item(), response=response)
            exhibitor_item.add_value("exhibitor_name", exhibitor_name)
            yield exhibitor_item.load_item()
