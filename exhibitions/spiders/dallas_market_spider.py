import datetime
from urllib.parse import urlencode

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse, Request

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class DallasMarketSpider(BaseSpider):
    name = "DallasMarketSpider"

    EXHIBITION_DATE = datetime.date(2022, 6, 1)
    EXHIBITION_NAME = "Dallas Market - Lightovation"
    EXHIBITION_WEBSITE = "https://dallasmarketcenter.com/markets/lightovation"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    EXHIBITORS_LIST_API = "https://dallasmarketcenter.com/lines/get-lines.aspx"
    EXHIBITORS_DETAILS_URL = (
        "https://dallasmarketcenter.com/exhibitors/detail.aspx?exhibitor={exhibitor_id}"
    )

    URLS = [EXHIBITORS_LIST_API]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    default_page_size = 1000

    params = {
        "buildings": "7,4,1",
        "pageNumber": 1,
        "pageSize": default_page_size,
        "sortBy": "Line",
        "sortOrder": "ASC",
    }

    def format_request(self):
        return Request(
            url=f"{self.EXHIBITORS_LIST_API}?{urlencode(self.params)}",
            headers=self.HEADERS,
            callback=self.fetch_exhibitors,
        )

    def fetch_exhibitors(self, response: TextResponse):
        response_json: dict = response.json()
        current_page: int = response_json.get("page")
        all_pages: int = response_json.get("pages")
        exhibitors_set: set = response.meta.get("exhibitors_set", set())
        exhibitors_set.update(
            set(SelectJmes("lines[].exhibitorId")(response_json)) or set()
        )
        if current_page != all_pages:
            new_params = self.params.copy()
            new_params["pageNumber"] = current_page + 1
            yield response.follow(
                url=f"{self.EXHIBITORS_LIST_API}?{urlencode(new_params)}",
                callback=self.fetch_exhibitors,
                headers=response.request.headers,
                meta={**response.meta, "exhibitors_set": exhibitors_set},
            )
        else:
            rows: int = response_json.get("rows")
            self.logger.info(
                f"Crawled {len(exhibitors_set)} exhibitors from {rows} lines."
            )
            for exhibitor_id in exhibitors_set:
                yield response.follow(
                    url=self.EXHIBITORS_DETAILS_URL.format(exhibitor_id=exhibitor_id),
                    headers=response.request.headers,
                    callback=self.parse_exhibitors,
                )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath(
            "exhibitor_name", '//*[@class="exhibitor-name"]/text()'
        )
        exhibitor_item.add_xpath(
            "booth_number", '//*[@class="exhibitor-label"]//text()'
        )
        exhibitor_item.add_xpath(
            "address",
            '//div[contains(@class, "main-contact-info")]//div[@itemprop="address"]//text()',
        )
        exhibitor_item.add_xpath("category", '//td[@class="category"]/span/text()')
        exhibitor_item.add_xpath("brands", '//span[@itemprop="brand"]/text()')
        exhibitor_item.add_xpath("description", '//p[@itemprop="description"]/text()')
        exhibitor_item.add_xpath(
            "website",
            '//div[contains(@class, "main-contact-info")]//a[contains(@id, "CompanyWebsite")]/text()',
        )
        exhibitor_item.add_xpath(
            "email",
            '//div[contains(@class, "main-contact-info")]//a[@id="primaryemail"]/text()',
        )
        exhibitor_item.add_xpath(
            "phone",
            '//div[contains(@class, "main-contact-info")]//p[@itemprop="telephone"]/text()',
        )
        # replace with method parse exhibitors data
        yield exhibitor_item.load_item()
