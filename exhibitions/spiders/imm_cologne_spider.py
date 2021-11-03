import datetime
import json

from itemloaders.processors import SelectJmes
from urllib.parse import urlencode

from scrapy import Request
from scrapy.http import Response

from exhibitions.constants import PROXY_ZYTE
from exhibitions.item_loaders.imm_cologne_loader import ImmCologneLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class ImmCologneSpider(BaseSpider):
    name = "ImmCologneSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 17)
    EXHIBITION_NAME = "imm cologne"
    EXHIBITION_WEBSITE = "https://www.imm-cologne.com/"

    HEADERS = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "dnt": 1,
        "pragma": "no-cache",
        "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    }

    item_loader = ImmCologneLoader
    item = ExhibitorItem

    EXHIBITORS_LIST_URL = (
        "https://www.imm-cologne.com/imm-cologne-exhibitors/list-of-exhibitors/"
    )

    URLS = [
        EXHIBITORS_LIST_URL,
    ]

    exhibitors_query_params = {
        "start": 0,
        "dat": 21823,
        "sortAby": "-",
    }

    PROXY = PROXY_ZYTE

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "exhibitions.middlewares.proxy_middleware.ProxyDownloaderMiddleware": 0,
        },
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    def format_request(self):
        return Request(
            url=f"{self.EXHIBITORS_LIST_URL}?{urlencode(self.exhibitors_query_params)}",
            callback=self.fetch_exhibitors,
            headers=self.HEADERS,
        )

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath(
            '//div[@id="pagecontent"]//a[@class="initial_noline"]'
        )
        yield from response.follow_all(
            exhibitors,
            callback=self.parse_exhibitors,
            headers=self.HEADERS,
        )
        next_url = response.xpath('//a[@class="slick-next"]/@href').get()
        if next_url:
            yield response.follow(
                url=next_url, callback=self.fetch_exhibitors, headers=self.HEADERS
            )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath("exhibitor_name", "//h1/text()")
        stand_hall_lines = response.xpath(
            '//a[@title="Hall Stand"]/span/text()'
        ).getall()
        halls, booths = set(), set()
        for line in stand_hall_lines:
            line_formatted = line.strip()
            if not line_formatted:
                continue
            hall, booth = line_formatted.split(" | ")
            halls.add(hall)
            booths.add(booth)
        exhibitor_item.add_value("booth_number", booths)
        exhibitor_item.add_value("hall_location", halls)
        address_lines: str = response.xpath('//div[@class="cont"]//text()').getall()
        if address_lines:
            address_lines_filtered = list(filter(lambda x: x.strip(), address_lines))
            exhibitor_item.add_value("address", address_lines_filtered[:-1])
            exhibitor_item.add_value("country", address_lines_filtered[-1])
        categories_raw_json = response.xpath(
            '//div[@class="accordeonlist"]/ul[@class="level-1"]/text()'
        ).get()
        try:
            categories_json = json.loads(categories_raw_json)
            exhibitor_item.add_value(
                "category", SelectJmes("*.children.*.text[]")(categories_json)
            )
        except (json.JSONDecodeError, TypeError):
            pass
        exhibitor_item.add_xpath(
            "brands", '//p[contains(b/text(), "Brands")]/following-sibling::div//text()'
        )
        exhibitor_item.add_xpath(
            "website", '//div[contains(@class, "ico_link")]//text()'
        )
        exhibitor_item.add_xpath(
            "email", '//div[contains(@class, "ico_email")]//text()'
        )
        exhibitor_item.add_xpath(
            "phone", '//div[contains(@class, "ico_phone")]//text()'
        )
        exhibitor_item.add_xpath("fax", '//div[contains(@class, "ico_fax")]//text()')
        # replace with method parse exhibitors data
        yield exhibitor_item.load_item()
