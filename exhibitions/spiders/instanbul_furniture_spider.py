import datetime

from scrapy import Selector
from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class InstanbulFurnitureSpider(BaseSpider):
    name = "InstanbulFurnitureSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 25)
    EXHIBITION_NAME = "Istanbul Furniture Fair"
    EXHIBITION_WEBSITE = "https://www.istanbulfurniturefair.com"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.istanbulfurniturefair.com/exhibitor-list",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        # exhibitor_urls = response.xpath("//a[contains(@class, 'detail-button')]/@href")
        # for exhibitor_url in exhibitor_urls:
        #     yield response.follow(
        #         url=exhibitor_url,
        #         callback=self.parse_exhibitors,
        #         headers=self.HEADERS
        #     )
        exhibitors = response.xpath("//div[@class='filter-list__item']")
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(response, exhibitor)
        next_page = response.xpath("//a[@class='next']/@href").get()
        if next_page:
            yield response.follow(
                url=next_page, callback=self.fetch_exhibitors, headers=self.HEADERS
            )

    def parse_exhibitor(self, response: Response, parent_selector: Selector):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_value(
            "exhibitor_name",
            parent_selector.xpath(".//td[@data-title='Firma Adı']/div[1]/text()").get(),
        )
        exhibitor_item.add_value(
            "phone",
            parent_selector.xpath(
                ".//td[@data-title='İletişim']//a[contains(@href, 'tel:')]/text()"
            ).get(),
        )
        exhibitor_item.add_value(
            "website",
            parent_selector.xpath(
                ".//td[@data-title='İletişim']//span[contains(text(), 'Web')]/following-sibling::a/text()"
            ).get(),
        )
        exhibitor_item.add_value(
            "address",
            parent_selector.xpath(".//td[@data-title='Firma Adı']/div[2]/text()").get(),
        )
        exhibitor_item.add_value(
            "hall_location",
            parent_selector.xpath(".//div[contains(@class, 'salon')]/text()").re_first(
                r"Hall:\s([\w\/]*)"
            ),
        )
        exhibitor_item.add_value(
            "booth_number",
            parent_selector.xpath(".//div[contains(@class, 'stand')]/text()").re_first(
                r"Stand:\s([\w\/]*)"
            ),
        )
        return exhibitor_item.load_item()
