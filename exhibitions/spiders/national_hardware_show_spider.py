import datetime
from typing import Dict

from itemloaders.processors import SelectJmes
from scrapy import Request
from scrapy.http import Response

from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


class NationalHardwareShowSpider(BaseSpider):
    name = "NationalHardwareShowSpider"

    EXHIBITION_DATE = datetime.date(2022, 4, 5)
    EXHIBITION_NAME = "National Hardware Show"
    EXHIBITION_WEBSITE = "https://www.nationalhardwareshow.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader  # create new and replace with class name

    URLS = [
        "https://xd0u5m6y4r-dsn.algolia.net/1/indexes/event-edition-eve-c12a3293-729f-40f3-aa85-0531383f3873_en-us/"
        "query"
        "?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.27.1"
        "&x-algolia-application-id=XD0U5M6Y4R"
        "&x-algolia-api-key=d5cd7d4ec26134ff4a34d736a7f9ad47",
    ]

    FORM_POST_BODY = """{{"params": "page={page}"}}"""

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        for url in self.URLS:
            yield Request(
                url=url,
                method="POST",
                body=self.FORM_POST_BODY.format(page=0),
                headers=self.HEADERS,
                callback=self.fetch_exhibitors,
            )

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: Dict):
        exhibitors = SelectJmes("hits[]")(response_json)
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(response, exhibitor)
        page = response_json.get("page")
        if page < response_json.get("nbPages"):
            yield response.follow(
                url=response.url,
                method="POST",
                body=self.FORM_POST_BODY.format(page=page + 1),
                headers=self.HEADERS,
                callback=self.fetch_exhibitors,
            )

    def parse_exhibitor(self, response: Response, exhibitor_info: Dict):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_item.add_value("exhibitor_name", exhibitor_info.get("companyName"))
        exhibitor_item.add_value("exhibitor_name", exhibitor_info.get("companyName"))
        exhibitor_item.add_value(
            "brands",
            SelectJmes("representedBrands[].value")(exhibitor_info)
            or SelectJmes("representedBrands")(exhibitor_info),
        )
        exhibitor_item.add_value("category", SelectJmes("ppsAnswers")(exhibitor_info))
        exhibitor_item.add_value(
            "description",
            SelectJmes("description.value")(exhibitor_info)
            or exhibitor_info.get("description"),
        )
        exhibitor_item.add_value("booth_number", exhibitor_info.get("standReference"))
        exhibitor_item.add_value("country", exhibitor_info.get("locale"))
        exhibitor_item.add_value("website", exhibitor_info.get("website"))
        exhibitor_item.add_value("phone", exhibitor_info.get("phone"))
        exhibitor_item.add_value("email", exhibitor_info.get("email"))
        return exhibitor_item.load_item()
