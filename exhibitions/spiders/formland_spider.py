import datetime
import re

from scrapy.http import TextResponse

from exhibitions.item_loaders.formland_loader import FormLandItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


HALL_REGEX = re.compile(r"Hall:\s(?P<hall>.*)")
STAND_REGEX = re.compile(r"Stand:\s(?P<stand>.*)")


class FormLandSpider(BaseSpider):
    name = "FormLandSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 2)
    EXHIBITION_NAME = "Formland - January"
    EXHIBITION_WEBSITE = "https://www.formland.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = FormLandItemLoader
    item = ExhibitorItem

    # The page size is an upper bound - see Show All button in the pagination
    PAGE_SIZE = 10000
    EXHIBITORS_LIST_URL = f"https://www.formland.com/exhibitor-catalogue/see-all-exhibitors?PageSize={PAGE_SIZE}"

    URLS = [EXHIBITORS_LIST_URL]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath(
            "//div[contains(@class, 'e-productlist')]//li//a/@href"
        ).getall()
        yield from response.follow_all(
            exhibitors, callback=self.parse_exhibitors, headers=self.HEADERS
        )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", "//h1/a/text()")
        show_locations: list = response.xpath(
            "//div[@class='text-center']/h3[@class='mt-1']/text()"
        ).getall()
        show_location: str = "".join(show_locations)
        exhibitor_item.add_value(
            "hall_location", HALL_REGEX.search(show_location).group("hall")
        )
        exhibitor_item.add_value(
            "booth_number", STAND_REGEX.search(show_location).group("stand")
        )
        exhibitor_item.add_xpath(
            "manufacturers",
            "//h3[contains(text(), 'Represented companies')]/following-sibling::p/text()",
        )
        exhibitor_item.add_xpath(
            "brands",
            "//h3[contains(text(), 'Represented brands')]/following-sibling::p/text()",
        )
        exhibitor_item.add_xpath(
            "category", "//span[@class='catalogue-update-product-group-wrapper']/text()"
        )
        exhibitor_item.add_xpath(
            "description", "//div[@class='span12 mt-2 mb-2']/p/text()"
        )
        address: str = response.xpath("//div[@class='span5 text-right']/p/text()").get(
            ""
        )
        exhibitor_item.add_value("address", address.rstrip(", "))
        exhibitor_item.add_value("country", address.split(",")[-1])
        exhibitor_item.add_xpath("website", "//div[@class='span5 text-right']/a/@href")
        return exhibitor_item.load_item()
