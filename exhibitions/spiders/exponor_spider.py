import datetime
import re

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class ExponorSpider(BaseSpider):
    name = "ExponorSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 3)
    EXHIBITION_NAME = "Exponor"
    EXHIBITION_WEBSITE = "https://exporthome.exponor.pt/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://exporthome.exponor.pt/expositor/lista-de-expositores-2019/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        with open("debug.html", "w") as f:
            f.write(response.text)

        html_exhibitors_raw = response.xpath(
            '//div[contains(@class, "pedido-expositor-container")]//p'
        ).get()
        exhibitors_raw = re.sub(r"<.*?>", "", html_exhibitors_raw)
        exhibitors = exhibitors_raw.splitlines()

        for exhibitor_name in exhibitors:
            if not exhibitor_name:
                continue

            exhibitor_item = self.item_loader(item=self.item(), response=response)
            exhibitor_item.add_value("exhibitor_name", exhibitor_name)
            yield exhibitor_item.load_item()
