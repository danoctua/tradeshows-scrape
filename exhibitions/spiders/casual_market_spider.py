import datetime

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class TemplateSpider(BaseSpider):
    name = "CasualMarketSpider"

    EXHIBITION_DATE = datetime.date(2021, 9, 21)
    EXHIBITION_NAME = "Chicago Casual Market"
    EXHIBITION_WEBSITE = "https://www.casualmarket.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader  # create new and replace with class name

    URLS = [
        "https://www.casualmarket.com/showrooms-exhibitors/showroom-and-exhibitor-listing",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath('//div[contains(@class, "detail")]')
        for exhibitor in exhibitors:
            exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
            exhibitor_item.add_value("exhibitor_name", exhibitor.xpath(".//a/text()").get())
            booth_number, phone = exhibitor.xpath(".//div[@class='col-xs-12 col-sm-3']/text()").getall()[:2]
            exhibitor_item.add_value("booth_number", booth_number)
            exhibitor_item.add_value("phone", phone)
            yield exhibitor_item.load_item()

    def parse_exhibitors(self, response: Response):
        # replace with method parse exhibitors data
        pass
