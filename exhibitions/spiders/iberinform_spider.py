import datetime

from scrapy.http import TextResponse

from exhibitions.constants import PROXY_BRIGHT_DATA
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class IberinformSpider(BaseSpider):
    name = "IberinformSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 28)
    EXHIBITION_NAME = "iberinform"
    EXHIBITION_WEBSITE = "https://www.iberinform.es/informacion-de-empresas/directorio-cnae/310/fabricacion-de-muebles"

    HEADERS = {
        "Host": "www.iberinform.es",
        "Upgrade-Insecure-Requests": 1,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-GPC": 1,
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-GB,en;q=0.9",
    }

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.iberinform.es/informacion-de-empresas/directorio-cnae/3109/fabricacion-de-otros-muebles",
    ]

    PROXY = PROXY_BRIGHT_DATA

    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # "exhibitions.middlewares.proxy_middleware.ProxyDownloaderMiddleware": 0,
            # "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": 5,
        },
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
        # "COOKIES_ENABLED": True,
        # "DOWNLOAD_DELAY": 0.5,
    }

    def fetch_exhibitors(self, response: TextResponse):

        exhibitors = response.xpath("//tbody/tr")
        for exhibitor_row in exhibitors:

            name_column, country_column, address_column, *_ = exhibitor_row.xpath(
                ".//td"
            )
            exhibitor = name_column.xpath(".//h3/a")

            yield response.follow(
                url=exhibitor.xpath("./@href").get(),
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
                meta={
                    **response.meta,
                    "exhibitor_name": exhibitor.xpath("./text()").get(),
                    "country": country_column.xpath("./text()").get(),
                    "address": address_column.xpath("./text()").get(),
                },
            )
        next_page = response.xpath(
            '//ul[@class="pagination"]//a[@aria-label="Next"]/@href'
        ).get()
        if next_page:
            yield response.follow(
                url=next_page,
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

    def parse_exhibitors(self, response: TextResponse):
        # with open("debug.html", "w") as f:
        #     f.write(response.text)
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_xpath(
            "exhibitor_name", "//h2[@class='title-company']/text()"
        )
        exhibitor_item.add_value("exhibitor_name", response.meta["exhibitor_name"])
        exhibitor_item.add_xpath(
            "address",
            '//ul[@class="company-data"]/li[contains(./span/text(), "Dirección de")]/div[@class="info"]//text()',
        )
        exhibitor_item.add_value("country", response.meta["country"])
        exhibitor_item.add_value("address", response.meta["address"])
        exhibitor_item.add_xpath(
            "website",
            '//ul[@class="company-data"]/li[contains(./span/text(), "Sitio web")]/div[@class="info"]//text()',
        )
        return exhibitor_item.load_item()
