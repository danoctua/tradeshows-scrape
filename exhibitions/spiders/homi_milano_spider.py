import datetime
import re
from typing import Optional

import scrapy
from scrapy.http import TextResponse

from exhibitions.constants import PROXY_ZYTE
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class HomiMilanoSpider(BaseSpider):
    name = "HomiMilanoSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 23)
    EXHIBITION_NAME = "Homi Milano"
    EXHIBITION_WEBSITE = "http://www.bilbaomueble.com/"

    HEADERS = {
        "Accept": "*/*",
        "Accept-Encoding": "zip, deflate, br",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Sec-GPC": 1,
        "Host": "expoplaza-homi.fieramilano.it",
        "Origin": "https://expoplaza-homi.fieramilano.it",
        "Connection": "keep-alive",
    }

    item_loader = BaseItemLoader
    item = ExhibitorItem

    GET_EXHIBITORS_INITIAL_URL: str = (
        "https://expoplaza-homi.fieramilano.it/en/exhibitors"
    )
    LIST_EXHIBITORS_URL: str = (
        "https://expoplaza-homi.fieramilano.it/en/search/exhibitors"
    )
    REQUEST_TOKEN_REGEX = re.compile(
        r"'requestObject': searchObject, 'token': '(?P<request_token>.*)'"
    )
    token: str
    cookies: str

    URLS = [GET_EXHIBITORS_INITIAL_URL]

    PROXY = PROXY_ZYTE

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "exhibitions.middlewares.proxy_middleware.ProxyDownloaderMiddleware": 0,
            "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 5,
        },
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
        "COOKIES_ENABLED": True,
        "COOKIES_DEBUG": True,
        "DOWNLOAD_DELAY": 0.5,
    }

    COOKIE_JAR = "cookiejar"

    def start_requests(self):
        yield scrapy.Request(
            url=self.GET_EXHIBITORS_INITIAL_URL,
            headers=self.HEADERS,
            meta={"cookiejar": self.COOKIE_JAR},
            callback=self.fetch_exhibitors,
        )

    def _get_request_body(self, offset: int = 1) -> dict:
        return {
            "requestObject[exhibitorName]": "",
            "requestObject[category][name]": "",
            "requestObject[offset]": str(offset),
            "token": self.token,
        }

    def fetch_exhibitors(self, response: TextResponse):
        token_search = self.REQUEST_TOKEN_REGEX.search(response.text)
        if token_search:
            self.token = token_search.group("request_token")
        return self.fetch_additional_exhibitors(response)

    def fetch_additional_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath("//*[@class='exhibitor-name']/a/@href").getall()
        for exhibitor in exhibitors:
            yield response.follow(
                url=f"{exhibitor}/info",
                callback=self.parse_exhibitors,
                meta=response.meta,
                headers=self.HEADERS,
                cookies=response.request.cookies,
            )
        current_offset = response.meta.get("offset", 0)
        yield scrapy.FormRequest(
            url=self.LIST_EXHIBITORS_URL,
            formdata=self._get_request_body(offset=current_offset + 1),
            meta={**response.meta, "offset": current_offset + 1},
            callback=self.fetch_additional_exhibitors,
            headers=self.HEADERS,
        )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath(
            "exhibitor_name", "//*[@class='exhibitor-name']/text()"
        )
        stand = response.xpath(
            "//*[contains(@class, 'padiglione-wrap')]/span/text()"
        ).getall()
        if len(stand) == 2:
            hall_location, booth_number = stand
            exhibitor_item.add_value("hall_location", hall_location.rstrip(" -"))
            exhibitor_item.add_value("booth_number", booth_number)
        exhibitor_item.add_value(
            "address",
            [
                self._get_attribute_by_label(response, label)
                for label in ["City", "Address"]
            ],
        )
        exhibitor_item.add_value(
            "country", self._get_attribute_by_label(response, "Country")
        )
        exhibitor_item.add_value(
            "phone", self._get_attribute_by_label(response, "Phone")
        )
        exhibitor_item.add_value("fax", self._get_attribute_by_label(response, "Fax"))
        exhibitor_item.add_value(
            "email", self._get_attribute_by_label(response, "Email")
        )
        exhibitor_item.add_value(
            "website", self._get_attribute_by_label(response, "Website")
        )
        yield exhibitor_item.load_item()

    @staticmethod
    def _get_attribute_by_label(response: TextResponse, label: str) -> Optional[str]:
        output: str = response.xpath(
            f"//*[@class='exhibitor-info-entry']/div[contains(text(), '{label}')]/following-sibling::div//text()"
        ).extract_first()
        # filter out empty values
        return output if output not in ("", "-") else None
