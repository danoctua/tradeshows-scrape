import datetime
import json
import re
from typing import Optional

import scrapy
from scrapy.http import Response

from exhibitions.item_loaders.domotex_item_loader import DomotexItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider

LOCATION_REGEX = re.compile(r"Hall (?P<hall>.*), Stand (?P<stand>.*)")
PHONE_REGEX = re.compile(r"Phone: (?P<value>.*)")
FAX_REGEX = re.compile(r"Fax: (?P<value>.*)")


class DomotexSpider(BaseSpider):
    name = "DomotexSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 13)
    EXHIBITION_NAME = "domotex"
    EXHIBITION_WEBSITE = "https://www.domotex.de"

    HEADERS = {
        "Upgrade-Insecure-Requests": 1,
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-GPC": 1
    }

    item_loader = DomotexItemLoader
    item = ExhibitorItem

    MAIN_SEARCH_URL = "https://www.domotex.de/en/search/?category=ep"

    URLS = [MAIN_SEARCH_URL]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    @staticmethod
    def get_post_data(page_number: int, page_state: Optional[str]) -> dict:
        return {
            "action": f'{{"action":"page","value":"{page_number}"}}',
            "category": "ep",
            "state": page_state,
            "search": ""
        }

    def start_requests(self):
        for url in self.URLS:
            yield scrapy.Request(
                url=url,
                callback=self.fetch_exhibitors,
                headers=self.HEADERS
            )

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath(
            "//o-search-snippet[@type='Exhibitor 2022']/@href"
        ).getall()
        for exhibitor_url in exhibitors:
            yield response.follow(
                url=exhibitor_url,
                callback=self.parse_exhibitors,
                headers=self.HEADERS
            )
        if not exhibitors:
            with open("dnt.html", "w") as f:
                f.write(response.text)
        next_page = response.xpath(
            "//a[@data-action='page']/i[contains(@class, 'icon-bracket-right')]/parent::a/@data-value"
        ).get()
        page_state = response.xpath("//input[@name='state']/@value").get()
        if next_page:
            print("POST DATA", self.get_post_data(next_page, page_state))
            yield scrapy.FormRequest(
                url=self.MAIN_SEARCH_URL,
                method="POST",
                formdata=self.get_post_data(next_page, page_state),
                headers=self.HEADERS,
                callback=self.fetch_exhibitors
            )

    def parse_exhibitors(self, response: Response):
        # replace with method parse exhibitors data
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath(
            "exhibitor_name",
            "//c-page-intro//template[@slot='headline']//h1[contains(@class, 'as-headline')]/text()"
        )
        location = response.xpath(
            "//c-page-intro//template[@slot='description']//div[contains(@class, 'cell')]//*[@class='as-content']//span[contains(./text(), Hall)]"
        ).get("")
        location_search = LOCATION_REGEX.search(location)
        if location_search:
            exhibitor_item.add_value("booth_number", location_search.group("stand"))
            exhibitor_item.add_value("hall_location", location_search.group("hall"))

        exhibitor_item.add_xpath(
            "description",
            "//c-detail-profil//p/text()"
        )
        contact_container = response.xpath("//c-navigation-tabs-dynamic//*[contains(@class, 'contact-container')]/div")
        exhibitor_item.add_value("address", contact_container.xpath("./div[1]//ul/li/text()").getall())
        exhibitor_item.add_value("country", contact_container.xpath("./div[1]//ul/li/text()").getall())
        exhibitor_item.add_value("website", contact_container.xpath("./div[1]//a/@href").get())
        exhibitor_item.add_value(
            "phone",
            contact_container.xpath("./div[2]//ul/li[contains(text(), 'Phone')]/text()").re_first(PHONE_REGEX)
        )
        exhibitor_item.add_value(
            "fax",
            contact_container.xpath("./div[2]//ul/li[contains(text(), 'Fax')]/text()").re_first(FAX_REGEX)
        )

        return exhibitor_item.load_item()
