import datetime
from typing import Optional

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class MadeInCanadaSpider(BaseSpider):
    name = "MadeInCanadaSpider"

    EXHIBITION_DATE = datetime.date(2021, 11, 10)
    EXHIBITION_NAME = "Made in Canada"
    EXHIBITION_WEBSITE = "https://madeinca.ca/blog"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://madeinca.ca/blog",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath('//h2[@class="entry-title"]/a/@href')
        for exhibitor in exhibitors:
            yield response.follow(
                url=exhibitor,
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
            )

        next_page: Optional[str] = response.xpath('//a[contains(@class, "next")]/@href').get()
        if next_page:
            yield response.follow(
                url=next_page,
                callback=self.fetch_exhibitors,
                headers=self.HEADERS
            )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_name = response.xpath('//*[@class="entry-content"]/p[contains(.//text(), "Name")]/text()').get()
        # alternative path if the name was not preformatted right
        if not exhibitor_name:
            exhibitor_name = response.xpath('//*[@class="entry-content"]/p[contains(.//text(), "Name")]/text()').get("")
            exhibitor_name = exhibitor_name.split(":")[-1]
        exhibitor_item.add_value("exhibitor_name", exhibitor_name)
        exhibitor_item.add_xpath("exhibitor_name", '//h1[@class="entry-title"]/text()')
        exhibitor_item.add_xpath("category", '//*[@class="entry-content"]/p[contains(.//text(), "Products")]/text()')
        exhibitor_item.add_xpath("website", '//*[@class="entry-content"]/p[contains(.//text(), "Website")]/a/@href')
        exhibitor_item.add_xpath("description", '//*[@class="entry-content"]/p[not(b) and not(strong)][1]')
        yield exhibitor_item.load_item()
