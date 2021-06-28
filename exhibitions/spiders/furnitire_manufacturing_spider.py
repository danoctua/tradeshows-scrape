import datetime

from scrapy.http import Response

from exhibitions.spiders.base_spider import BaseSpider
from exhibitions.item_loaders.furniture_manufacturer_loader import FurnitureManufacturerItemLoader
from exhibitions.items.exhibitor import ExhibitorItem


class FurnitureManufacturingSpider(BaseSpider):
    name = "FurnitureManufacturingSpider"

    EXHIBITION_DATE = datetime.date(2021, 7, 20)
    EXHIBITION_NAME = "Furniture Manufacturing Expo"
    EXHIBITION_WEBSITE = "https://www.furnituremanufacturingexpo.com/"

    ONLY_FIELDS = (
        "exhibitor_name",
        "booth_number",
        "exhibitor_url",
        "category",
        "address",
        "description",
        "website",
        "instagram",
        "facebook",
        "twitter",
        "linkedin"
    )

    item_loader = FurnitureManufacturerItemLoader

    URLS = [
        "https://www.furnituremanufacturingexpo.com/who-should-attend/-exhibitors-list",
        "https://www.furnituremanufacturingexpo.com/who-should-attend/-exhibitors-list?page=2&searchgroup=8A47C7CE-exhibitors"
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath("//a[contains(@class, 'list__items__item__title__link')]")
        for exhibitor in exhibitors:
            yield response.follow(exhibitor, callback=self.parse_exhibitors)

    def parse_exhibitors(self, response: Response):
        item = self.item_loader(item=ExhibitorItem(), response=response)
        item.add_value("exhibitor_url", response.url)
        item.add_xpath("exhibitor_name", '//h1[@class="m-exhibitor-entry__item__header__infos__title"]/text()')
        booth = response.xpath(
            '//div[@class="m-exhibitor-entry__item__header__infos__stand"]/text()'
        ).re_first(r"Booth:\s(.\d+)")
        item.add_value("booth_number", booth)
        item.add_xpath("category", '//li[@class="m-exhibitor-entry__item__header__infos__categories__item"]/text()')
        item.add_xpath("description", '//div[@class="m-exhibitor-entry__item__body__description"]/p/text()')
        item.add_xpath("address", '//div[@class="m-exhibitor-entry__item__body__contacts__address"]/text()')
        item.add_xpath("website",
                       '//div[@class="m-exhibitor-entry__item__body__contacts__additional__button__website"]/a/@href')
        for social in ("instagram", "facebook", "twitter", "linkedin"):
            item.add_xpath(
                social,
                f'//li[@class="m-exhibitor-entry__item__body__contacts__additional__social__item"]/a[contains(@href, "{social}")]/@href'
            )
        yield item.load_item()


