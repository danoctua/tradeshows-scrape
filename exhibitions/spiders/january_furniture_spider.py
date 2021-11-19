import datetime
import json

import scrapy
from scrapy.http import Response, TextResponse
from scrapy.utils.python import to_bytes

from exhibitions.constants import PROXY_ZYTE
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class JanuaryFurnitureSpider(BaseSpider):
    name = "JanuaryFurnitureSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 23)
    EXHIBITION_NAME = "January Furniture Show"
    EXHIBITION_WEBSITE = "https://januaryfurnitureshow.com"

    HEADERS = {}

    item_loader = BaseItemLoader
    item = ExhibitorItem

    current_page: int = 1

    MAIN_URL = "https://januaryfurnitureshow.com/search/exhibitors"

    URLS = [MAIN_URL]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    def fetch_exhibitors(self, response: TextResponse):
        print(response.request.headers)
        with open("dnt.html", "w") as f:
            f.write(response.text)
        exhibitors = response.xpath(
            "//a[contains(@class, 'exhcard__img-link')]/@href"
        ).getall()
        if exhibitors:
            for exhibitor_url in exhibitors:
                yield response.follow(url=exhibitor_url, callback=self.parse_exhibitors)
            self.current_page += 1
            yield response.follow(
                url=f"{self.MAIN_URL}?page={self.current_page}",
                callback=self.fetch_exhibitors,
            )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath(
            "exhibitor_name",
            "//*[@class='expo-container']//*[@class='prodmodal__info-title']/text()",
        )
        address = response.xpath(
            "//*[@class='expo-container']//*[@class='prodmodal__info-location']/text()"
        ).get()
        if address:
            exhibitor_item.add_value("address", address)
            exhibitor_item.add_value("country", address.split(",")[-1].strip())
        exhibitor_item.add_xpath(
            "hall_location",
            "//*[@class='expo-container']//*[@class='prodmodal__info-details-item prodmodal__info-details-item_hall-stand']/span[contains(text(), 'Hall')]//following-sibling::*[1]/text()",
        )
        exhibitor_item.add_xpath(
            "booth_number",
            "//*[@class='expo-container']//*[@class='prodmodal__info-details-item prodmodal__info-details-item_hall-stand']/span[contains(text(), 'Stand')]//following-sibling::*[1]/text()",
        )
        exhibitor_item.add_xpath(
            "website",
            "//*[@class='expo-container']//*[@class='prodmodal__info-site']/a/@href",
        )
        exhibitor_item.add_xpath(
            "description", "//div[contains(@class, 'about-description')]//p//text()"
        )
        yield exhibitor_item.load_item()
