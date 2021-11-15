import datetime

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class GivingLivingSpider(BaseSpider):
    name = "GivingLivingSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 16)
    EXHIBITION_NAME = "Giving & Living"
    EXHIBITION_WEBSITE = "http://givingliving.co.uk"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "http://givingliving.co.uk/exhibitorlist/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath("//*[@class='listing-item']")
        for exhibitor in exhibitors:
            exhibitor_item = self.item_loader(self.item(), response)
            exhibitor_item.add_value(
                "exhibitor_name",
                exhibitor.xpath(".//*[@class='exh-name']/text()").get(),
            )
            exhibitor_item.add_value(
                "description", exhibitor.xpath(".//*[@class='exh-copy']/text()").get()
            )
            exhibitor_item.add_value(
                "booth_number",
                exhibitor.xpath(".//*[@class='exh-stand']/text()").re_first(
                    r"Stand.(\d*)"
                ),
            )
            exhibitor_item.add_value(
                "website", exhibitor.xpath(".//*[@class='exh-web']/a/@href").get()
            )
            yield exhibitor_item.load_item()

        next_page = response.xpath("//a[contains(@class, 'next')]/@href").get()
        if next_page:
            yield response.follow(
                url=next_page,
                callback=self.fetch_exhibitors,
            )
