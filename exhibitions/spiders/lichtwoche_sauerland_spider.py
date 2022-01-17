import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class LichtwocheSauerlandSpider(BaseSpider):
    name = "LichtwocheSauerlandSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 6)
    EXHIBITION_NAME = "LICHTWOCHE SAUERLAND"
    EXHIBITION_WEBSITE = "https://www.lichtwoche-sauerland.de/en/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.lichtwoche-sauerland.de/en/for-visitors/exhibitors/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath('//ul[@class="flex-list"]/li/a')
        for exhibitor in exhibitors:
            yield response.follow(
                url=exhibitor,
                callback=self.parse_exhibitors,
                meta={"exhibitor_name": exhibitor.xpath("./figure/img/@alt").get()},
            )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_name = response.xpath('//div[@class="name"]/text()').get(
            response.meta["exhibitor_name"]
        )
        exhibitor_item.add_value("exhibitor_name", exhibitor_name)
        exhibitor_item.add_xpath("phone", '//span[@class="phone"]//text()')
        exhibitor_item.add_xpath("fax", '//span[@class="fax"]//text()')
        exhibitor_item.add_xpath("email", '//span[@class="email"]//text()')
        exhibitor_item.add_xpath("website", '//span[@class="web"]//text()')
        exhibitor_item.add_xpath(
            "address", '//div[@class="besuchsadresse"]/span//text()'
        )
        exhibitor_item.add_xpath(
            "country", '//div[@class="besuchsadresse"]/span[@class="country"]//text()'
        )
        exhibitor_item.add_xpath("description", '//div[@class="description"]//text()')
        return exhibitor_item.load_item()
