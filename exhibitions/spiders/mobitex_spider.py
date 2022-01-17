import datetime

from scrapy.http import TextResponse

from exhibitions.constants import PROXY_ZYTE
from exhibitions.item_loaders.mobitex_item_loader import MobitexItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class MobitexSpider(BaseSpider):
    name = "MobitexSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 23)
    EXHIBITION_NAME = "Mobitex"
    EXHIBITION_WEBSITE = "https://www.ibvv.cz/en/"

    HEADERS = {}  # replace with headers dict

    item_loader = MobitexItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.ibvv.cz/en/event/mobitex/exhibitors?type=1",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    def fetch_exhibitors(self, response: TextResponse):

        exhibitors = response.xpath(
            '//article[@class="exhibitor-item"]//a[@class="name"]/@href'
        )
        yield from response.follow_all(urls=exhibitors, callback=self.parse_exhibitors)
        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page:
            print(f"NEXT PAGE {next_page}")
            yield response.follow(url=next_page, callback=self.fetch_exhibitors)

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_xpath(
            "exhibitor_name", '//div[@class="exhibitor-info"]//h1/text()'
        )
        exhibitor_item.add_xpath(
            "address", '//div[@class="exhibitor-address-info"]/text()'
        )
        exhibitor_item.add_xpath(
            "phone",
            '//div[contains(@class, "exhibitor-address-info")]//div[@class="item" and .//span[@class="heading"]/text() = "Phone:"]/div//text()',
        )
        exhibitor_item.add_xpath(
            "email",
            '//div[contains(@class, "exhibitor-address-info")]//div[@class="item" and .//span[@class="heading"]/text() = "E-mail:"]/a/text()',
        )
        exhibitor_item.add_xpath(
            "website",
            '//div[contains(@class, "exhibitor-address-info")]//div[@class="item" and .//span[@class="heading"]/text() = "Webpage:"]/a/text()',
        )

        location_raw = response.xpath(
            '//div[@class="map"]//span[@class="text-bold"]/text()'
        ).get()
        if location_raw:
            locations = location_raw.split(",")
            hall_locations, booths = set(), set()
            for location in locations:
                location_strings = location.split(" / ")
                booth_number, hall_location = location_strings
                hall_locations.add(hall_location)
                booths.add(booth_number)
            exhibitor_item.add_value("booth_number", booths)
            exhibitor_item.add_value("hall_location", hall_locations)

        return exhibitor_item.load_item()
