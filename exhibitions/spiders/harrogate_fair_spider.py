import datetime
import re

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


HALL_REGEX = re.compile(r"Hall (?P<hall_location>[^\s]*)")
BOOTH_REGEX = re.compile(r"Stand (?P<booth_number>[^\s]*)")
PHONE_REGEX = re.compile(r"Tel: (?P<phone>[\d\s\+]*)")
FAX_REGEX = re.compile(r"Fax: (?P<fax>[\d\s\+]*)")


class HarrogateFairSpider(BaseSpider):
    name = "HarrogateFairSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 16)
    EXHIBITION_NAME = "Harrogate Christmas & Gift"
    EXHIBITION_WEBSITE = "https://www.harrogatefair.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.harrogatefair.com/exhibitor_list.asp",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = set(response.xpath("//a[@class='broaditemlink']/@href").getall())
        for exhibitor_url in exhibitors:
            yield response.follow(
                url=exhibitor_url, callback=self.parse_exhibitors, headers=self.HEADERS
            )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", "//h2[@class='exhtitle']/text()")
        stand_location = response.xpath("//*[@id='standHeader']/h2/text()")
        exhibitor_item.add_value("booth_number", stand_location.re_first(BOOTH_REGEX))
        exhibitor_item.add_value("hall_location", stand_location.re_first(HALL_REGEX))
        exhibitor_item.add_xpath("address", "//*[@id='companyinfo2']/p/text()")
        exhibitor_item.add_xpath(
            "email", "//*[@id='companyinfo2']/p/a[contains(@href, 'mailto')]/text()"
        )
        exhibitor_item.add_xpath(
            "website",
            "//*[@id='companyinfo2']/p/a[not(contains(@href, 'mailto'))]/text()",
        )
        exhibitor_item.add_xpath(
            "brands", "//h2[contains(text(), 'Brand')]//following-sibling::*/text()"
        )
        exhibitor_item.add_xpath(
            "description",
            "//h2[contains(text(), 'Information')]//following-sibling::*/text()",
        )
        contact_lines = response.xpath("//*[@id='companyinfo2']/p//text()").getall()
        contact = "\n".join(contact_lines)
        phone_search = PHONE_REGEX.search(contact)
        if phone_search:
            exhibitor_item.add_value("phone", phone_search.group("phone"))
        fax_search = FAX_REGEX.search(contact)
        if fax_search:
            exhibitor_item.add_value("fax", fax_search.group("fax"))

        yield exhibitor_item.load_item()
