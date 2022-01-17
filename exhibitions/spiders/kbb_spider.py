import datetime

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class KBBSpider(BaseSpider):
    name = "KBBSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 6)
    EXHIBITION_NAME = "KBB"
    EXHIBITION_WEBSITE = "https://www.eisenwarenmesse.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    MAX_RECORDS_NUM: int = 300

    URLS = [
        f"https://api-connect.informamarkets.com/api/v1/editions/NAM22KBB/listings?page=1&limit={MAX_RECORDS_NUM}&lang=en",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors: list[dict] = SelectJmes("data.items")(response.json())
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(exhibitor=exhibitor, response=response)

    def parse_exhibitor(self, exhibitor: dict, response: TextResponse):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_value("exhibitor_name", exhibitor.get("title"))
        exhibitor_item.add_value("description", exhibitor.get("description"))
        exhibitor_item.add_value(
            "booth_number", SelectJmes("booths.*.booth_number")(exhibitor)
        )
        exhibitor_item.add_value(
            "hall_location", SelectJmes("booths.*.pavilion")(exhibitor)
        )
        exhibitor_item.add_value("address", SelectJmes("address.*")(exhibitor))
        exhibitor_item.add_value("country", SelectJmes("address.country")(exhibitor))
        exhibitor_item.add_value("website", SelectJmes("website_url")(exhibitor))
        exhibitor_item.add_value("category", SelectJmes("categories.*")(exhibitor))
        exhibitor_item.add_value(
            "phone", SelectJmes("company.contacts.phone")(exhibitor)
        )
        exhibitor_item.add_value(
            "email", SelectJmes("company.contacts.email")(exhibitor)
        )
        return exhibitor_item.load_item()
