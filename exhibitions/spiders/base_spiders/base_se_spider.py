import re

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.utils.request import RequestWithParams


class BaseSESpider(BaseSpider):

    API_LIST_URL: str = []
    SHOW_SLUG: str = ""  # overwrite this field

    FROM_NODE: str

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    HEADERS = {"Cookie": f"{SHOW_SLUG}#lang=en"}

    PAGE_SIZE = 50

    item_loader = BaseItemLoader
    item = ExhibitorItem

    def __init__(self, **kwargs) -> None:
        self.API_LIST_URL: str = (
            f"https://www.{self.SHOW_SLUG}.se/api/data/digitalstands/"
        )
        self.URLS = [self.API_LIST_URL]
        super().__init__(**kwargs)

    def _get_query_params(self, page: int = 0) -> dict:
        return {
            "fromNode": self.FROM_NODE,
            "standFilterCategory": "",
            "text": "",
            "pageSize": self.PAGE_SIZE,
            "pageIndex": page,
        }

    def _get_request(self, page: int = 0) -> RequestWithParams:
        return RequestWithParams(
            url=self.API_LIST_URL,
            params=self._get_query_params(page),
            callback=self.fetch_exhibitors,
            headers=self.HEADERS,
        )

    def start_requests(self):
        yield self._get_request()

    def fetch_exhibitors(self, response: TextResponse):
        response_json: dict = response.json()
        exhibitors = response_json["items"]
        for exhibitor in exhibitors:
            yield response.follow(
                url=exhibitor["ItemUrl"].replace(
                    "?sc_lang=sv-se", "?sc_lang=en"
                ),  # to force English
                callback=self.parse_exhibitors,
                meta={**response.meta, "exhibitor": exhibitor},
            )
        total_items = response_json["totalItems"]
        page_index = response_json["pageIndex"]
        if self.PAGE_SIZE * (page_index + 1) < total_items:
            yield self._get_request(page_index + 1)

    def parse_exhibitors(self, response: TextResponse):
        exhibitor = response.meta["exhibitor"]
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_value("exhibitor_name", exhibitor["DigitalStandName"])
        exhibitor_item.add_value(
            "address", SelectJmes("[Address,PostalCode,City]")(exhibitor)
        )
        exhibitor_item.add_xpath("country", "//span[@itemprop='addressCountry']/text()")
        exhibitor_item.add_value("website", exhibitor["Website"])
        exhibitor_item.add_value("email", exhibitor["Email"])
        exhibitor_item.add_value("phone", exhibitor["Phone"])
        exhibitor_item.add_value("booth_number", exhibitor["Stand"])
        exhibitor_item.add_xpath(
            "brands",
            "//h2[contains(text(), 'Trademarks')]/following-sibling::ul/li//text()",
        )
        exhibitor_item.add_xpath(
            "category",
            "//h2[contains(text(), 'Categories')]/following-sibling::ul/li/span/text()",
        )
        return exhibitor_item.load_item()
