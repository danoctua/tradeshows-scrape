import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class FurnitureManufacturersSpider(BaseSpider):
    name = "FurnitureManufacturersSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 11)
    EXHIBITION_NAME = "Furniture Manufacturers"
    EXHIBITION_WEBSITE = "https://www.bfm.org.uk/directory/furniture-manufacturers/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.bfm.org.uk/directory/furniture-manufacturers/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath("//div[@class='items-inner']/a/@href")
        for exhibitor in exhibitors:
            yield response.follow(
                url=exhibitor, headers=self.HEADERS, callback=self.parse_exhibitors
            )
        next_page = response.xpath(
            "//ol[@class='paging']/li[@class='next']/a/@href"
        ).get()
        if next_page:
            yield response.follow(
                url=next_page, headers=self.HEADERS, callback=self.fetch_exhibitors
            )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", "//div[@class='va']/h2/text()")
        exhibitor_item.add_xpath("description", "//div[@class='wysiwyg']//text()")
        exhibitor_item.add_xpath("address", "//div[@class='address-block']//text()")
        exhibitor_item.add_xpath("phone", "//div[@class='telephone']/a/text()")
        exhibitor_item.add_xpath("email", "//div[@class='email']/a/text()")
        exhibitor_item.add_xpath("website", "//div[@class='website']/a/text()")
        exhibitor_item.add_xpath(
            "category", "//nav[contains(@class, 'member-directory')]//li/a/text()"
        )
        yield exhibitor_item.load_item()
