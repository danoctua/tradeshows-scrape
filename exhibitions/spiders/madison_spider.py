import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class MadisonSpider(BaseSpider):
    name = "MadisonSpider"

    EXHIBITION_DATE = datetime.date(2022, 4, 5)
    EXHIBITION_NAME = "41 Madison (New York Tabletop) - Spring"
    EXHIBITION_WEBSITE = "https://41madison.com/"

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://41madison.com/showroom",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitor_urls = response.xpath('//a[@class="post_name"]/@href')
        yield from response.follow_all(
            urls=exhibitor_urls, callback=self.parse_exhibitors
        )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", "//h2/text()")
        exhibitor_item.add_xpath("hall_location", '//div[@class="floor"]/text()')
        exhibitor_item.add_xpath("phone", '//div[@class="phone"]/a/text()')
        exhibitor_item.add_xpath("email", '//div[@class="contact-email"]/a/text()')
        exhibitor_item.add_xpath("website", '//div[@class="website"]/a/text()')
        exhibitor_item.add_xpath(
            "description", '//div[contains(@class, "read-more-box")]/p/text()'
        )
        return exhibitor_item.load_item()
