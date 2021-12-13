import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class PartnertageSpider(BaseSpider):
    name = "PartnertageSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 1)
    EXHIBITION_NAME = "Partnertage"
    EXHIBITION_WEBSITE = "https://www.partnertage-ostwestfalen.de/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.partnertage-ostwestfalen.de/aussteller/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = "".join(
            response.xpath("//div[@class='entry-content']/p[1]//text()").getall()
        )
        for exhibitor in exhibitors.split("|"):
            item = self.item_loader(self.item(), response)
            item.add_value("exhibitor_name", exhibitor)
            yield item.load_item()
