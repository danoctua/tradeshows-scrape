import datetime
from urllib.parse import urlencode

from scrapy import Request
from scrapy.http import TextResponse

from exhibitions.item_loaders.for_garden_loader import ForGardenItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class ForGardenSpider(BaseSpider):
    name = "ForGardenSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 31)
    EXHIBITION_NAME = "For Garden"
    EXHIBITION_WEBSITE = "https://for-garden.cz/en/"

    item_loader = ForGardenItemLoader
    item = ExhibitorItem

    URL_BASE = "http://katalogy.abf.cz/exhibitors"

    URLS = [URL_BASE]
    LAST_PAGE_COUNT = 31

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def _get_url_with_query_params(self, page_number: int) -> str:
        """Method to get the request URL with the encoded query params."""
        query_params = {"cat": "218", "lang": "1", "pg": str(page_number)}
        return f"{self.URL_BASE}&{urlencode(query_params)}"

    def start_requests(self):
        for _ in self.URLS:
            yield Request(
                url=self._get_url_with_query_params(page_number=1),
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
                meta={"next_page": 2},
            )

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath(
            "//div[@class='page-content-exhibitor-name']/a/@href"
        )
        for exhibitor_url in exhibitors:
            yield response.follow(
                url=exhibitor_url,
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
            )
        next_page = response.meta["next_page"]
        if next_page <= self.LAST_PAGE_COUNT:
            yield response.follow(
                url=self._get_url_with_query_params(page_number=next_page),
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
                meta={"next_page": next_page + 1},
            )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", "//h2/text()")
        exhibitor_item.add_xpath(
            "address", "//tr[contains(./th/text(), 'Address')]/td/text()"
        )
        exhibitor_item.add_xpath(
            "country", "//tr[contains(./th/text(), 'Address')]/td/text()"
        )
        exhibitor_item.add_xpath(
            "phone", "//tr[contains(./th/text(), 'Phone')]/td/text()"
        )
        exhibitor_item.add_xpath(
            "email", "//tr[contains(./th/text(), 'E-mail')]/td/a/text()"
        )
        exhibitor_item.add_xpath(
            "website", "//tr[contains(./th/text(), 'WWW')]/td/a/text()"
        )
        exhibitor_item.add_xpath(
            "description", "//div[@class='extended-data-profile']/text()"
        )
        exhibitor_item.add_xpath(
            "category", "//div[contains(@class, 'extended-data-category')]//a/text()"
        )
        location = response.xpath(
            "//tr[contains(./th/text(), 'Location')]/td/text()"
        ).get()
        if (
            isinstance(location, str)
            and len(location_split := location.split("-")) == 2
        ):
            hall_location, booth_number = location_split
            exhibitor_item.add_value("hall_location", hall_location)
            exhibitor_item.add_value("booth_number", booth_number)
        return exhibitor_item.load_item()
