import datetime

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class EcommerceSpider(BaseSpider):
    name = "EcommerceSpider"

    EXHIBITION_DATE = datetime.date(2022, 9, 2)
    EXHIBITION_NAME = "ecommerceberlin"
    EXHIBITION_WEBSITE = "https://ecommerceberlin.com/about"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    DETAILS_COMPANY_URL = "https://api.eventjuicer.com/v1/public/hosts/ecommerceberlin.com/companies/{exhibitor_slug}"

    URLS = [
        "https://api.eventjuicer.com/v1/public/hosts/ecommerceberlin.com/allexhibitors",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        response_json = response.json()
        for exhibitor_slug in SelectJmes("data[].slug")(response_json):
            yield response.follow(
                url=self.DETAILS_COMPANY_URL.format(exhibitor_slug=exhibitor_slug),
                callback=self.parse_exhibitors,
            )

    def parse_exhibitors(self, response: TextResponse) -> dict:
        response_json = response.json()
        exhibitor = SelectJmes("data.profile")(response_json)
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_value(
            "exhibitor_name",
            [
                # sometimes name is not available, so the slug is being populated
                exhibitor["name"],
                SelectJmes("data.slug")(response_json),
            ],
        )
        exhibitor_item.add_value("description", exhibitor["about"])
        exhibitor_item.add_value("website", exhibitor["website"])
        exhibitor_item.add_value("country", exhibitor["countries"])
        exhibitor_item.add_value("category", exhibitor["keywords"])
        exhibitor_item.add_value(
            "booth_number", SelectJmes("data.instances[].formdata.ti")(response_json)
        )
        return exhibitor_item.load_item()
