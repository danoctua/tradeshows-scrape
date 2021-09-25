import re

from scrapy.http import Response

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.base_item_loaders.base_a2z_item_loader import (
    BaseA2ZItemLoader,
)
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.utils.exceptions import NoExhibitorException


class BaseA2ZSpider(BaseSpider):
    name = "BaseA2ZSpider"

    item_loader = BaseA2ZItemLoader

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath("//a[contains(@class, 'exhibitorName')]")
        for exhibitor in exhibitors:
            yield response.follow(
                exhibitor, callback=self.parse_exhibitors, headers=self.HEADERS
            )

    def parse_exhibitors(self, response: Response):
        uid = re.search(r"BoothID=(\d+)", response.url)
        uid = uid.group(0) if uid else None
        if not uid:
            raise NoExhibitorException("Can't get exhibitor ID from URL")
        item = self.item_loader(item=ExhibitorItem(), response=response)
        item.add_value("exhibitor_url", response.url)
        item.add_xpath("exhibitor_name", '//*[@id="eboothContainer"]//h1/text()')
        city = response.xpath('//*[@class="BoothContactCity"]/text()').extract_first()
        state = response.xpath('//*[@class="BoothContactState"]/text()').extract_first()
        country = response.xpath(
            '//*[@class="BoothContactCountry"]/text()'
        ).extract_first()
        item.add_value("address", [city, state, country])
        item.add_value("country", country)

        item.add_xpath("website", '//*[@id="BoothContactUrl"]/text()')
        item.add_xpath(
            "description",
            '//*[@id="eboothContainer"]//p[not(@id) and not(@class)]/text()',
        )
        item.add_xpath(
            "brands",
            '//*[@id="eboothContainer"]//p[not(@id) and @class="BoothBrands"]/text()',
        )
        item.add_xpath("category", '//li[@class="ProductCategoryLi"]/a/text()')

        booth_number = response.xpath(
            '//*[@id="eboothContainer"]/ul/li[1]/text()'
        ).re_first(r"(\d+)")
        item.add_value("booth_number", booth_number)
        yield item.load_item()
