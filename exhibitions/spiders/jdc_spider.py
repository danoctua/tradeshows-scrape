import datetime

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse

from exhibitions.item_loaders.jdc_item_loader import JDCItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class JDCSpider(BaseSpider):
    name = "JDCSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 29)
    EXHIBITION_NAME = "JDC"
    EXHIBITION_WEBSITE = "https://www.journeesdescollections.com/en/"

    HEADERS = {}  # replace with headers dict

    item_loader = JDCItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.journeesdescollections.com/app/cache/en_Exposants.json",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        for exhibitor in response.json():
            yield self.parse_exhibitor(exhibitor=exhibitor, response=response)

    def parse_exhibitor(self, exhibitor: dict, response: TextResponse) -> dict:
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_value("exhibitor_name", exhibitor["nom"])
        exhibitor_item.add_value("description", exhibitor["resume"])
        exhibitor_item.add_value("website", exhibitor["website"])
        exhibitor_item.add_value("email", exhibitor["email"])
        exhibitor_item.add_value("country", exhibitor["country"])
        exhibitor_item.add_value(
            "address", SelectJmes("[addresse, addresse1, addresse2]")(exhibitor)
        )

        stand = exhibitor["stand"]
        if stand:
            hall_location, booth_number = stand.split("-")
            exhibitor_item.add_value("hall_location", hall_location)
            exhibitor_item.add_value("booth_number", booth_number)

        exhibitor_item.add_value("category", SelectJmes("domaines[].nom")(exhibitor))

        return exhibitor_item.load_item()
