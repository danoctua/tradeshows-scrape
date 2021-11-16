import datetime

from scrapy.http import Response

from exhibitions.item_loaders.top_drawer_item_loader import TopDrawerItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class TopDrawerSpider(BaseSpider):
    name = "TopDrawerSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 16)
    EXHIBITION_NAME = "Top Drawer Spring"
    EXHIBITION_WEBSITE = "https://www.topdrawer.co.uk/"

    HEADERS = {}  # replace with headers dict

    item_loader = TopDrawerItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.topdrawer.co.uk/s-s-2-2-edition-exhibiting-brands?&categories=1F33EDE6-5056-B733-490CE9290DAF9BF0&searchgroup=00000001-s-s-2-2-edition-exhibiting-brands",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath(
            "//a[@class='m-exhibitors-list__items__item__header__title__link js-librarylink-entry']/@href"
        ).getall()
        for exhibitor_url in exhibitors:
            yield response.follow(
                url=exhibitor_url, callback=self.parse_exhibitors, headers=self.HEADERS
            )
        next_page = response.xpath(
            "//a[@class='pagination__list__item__link pagination__list__item__link--next']/@href"
        ).get()
        if next_page:
            yield response.follow(
                url=next_page, callback=self.fetch_exhibitors, headers=self.HEADERS
            )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath(
            "exhibitor_name",
            "//*[@class='m-exhibitor-entry__item__header__title']/text()",
        )
        exhibitor_item.add_xpath(
            "booth_number",
            "//*[@class='m-exhibitor-entry__item__header__stand']/text()",
        )
        exhibitor_item.add_xpath(
            "address",
            "//*[@class='m-exhibitor-entry__item__body__contacts__address']/text()",
        )
        exhibitor_item.add_xpath(
            "country",
            "//*[@class='m-exhibitor-entry__item__body__contacts__address']/text()",
        )
        exhibitor_item.add_xpath(
            "website",
            "//*[@class='m-exhibitor-entry__item__body__contacts__additional__website']/*[contains(text(), 'Website')]/following-sibling::a/@href",
        )
        exhibitor_item.add_xpath(
            "description",
            "//*[@class='m-exhibitor-entry__item__body__description__profile']/p//text()",
        )
        exhibitor_item.add_xpath(
            "category",
            "//*[contains(@class, 'm-libraries-products-list__items__item__header__title__link')]/text()",
        )
        yield exhibitor_item.load_item()
