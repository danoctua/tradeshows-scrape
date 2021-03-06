from typing import Dict, List, Optional

import scrapy
from itemloaders.processors import SelectJmes
from scrapy.http import Response, TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper

DEFAULT_EXHIBITOR_INFO_API = "https://{exhibition_code}.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorInfo&exhID={exhibitor_id}"
DEFAULT_EXHIBITOR_BOOTHS_API = "https://{exhibition_code}.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorBooths&exhID={exhibitor_id}"
DEFAULT_EXHIBITORS_LIST_API = "https://{exhibition_code}.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorNames"


class BaseMapYourShowSpider(BaseSpider):
    name = "BaseMapYourShowSpider"

    EXHIBITION_CODE: str

    HEADERS = {"X-Requested-With": "XMLHttpRequest"}

    item_loader = BaseItemLoader

    URLS = []

    EXHIBITOR_INFO_API: Optional[str] = None
    EXHIBITOR_BOOTHS_API: Optional[str] = None
    EXHIBITORS_LIST_API: Optional[str] = None

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url=(
                self.EXHIBITORS_LIST_API
                if self.EXHIBITORS_LIST_API
                else DEFAULT_EXHIBITORS_LIST_API.format(
                    exhibition_code=self.EXHIBITION_CODE
                )
            ),
            headers=self.HEADERS,
            callback=self.fetch_exhibitors,
        )

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: List[Dict]):
        for exhibitor_data in response_json:
            exhibitor_id = exhibitor_data.get("fieldvalue")
            if exhibitor_id:
                yield response.follow(
                    url=(
                        self.EXHIBITOR_INFO_API.format(exhibitor_id=exhibitor_id)
                        if self.EXHIBITOR_INFO_API
                        else DEFAULT_EXHIBITOR_INFO_API.format(
                            exhibitor_id=exhibitor_id,
                            exhibition_code=self.EXHIBITION_CODE,
                        )
                    ),
                    callback=self.parse_exhibitors,
                    headers=self.HEADERS,
                )

    def parse_exhibitors(self, response: TextResponse):
        response_json = response.json()
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_item.add_value(
            "exhibitor_name", SelectJmes("[].exhname")(response_json)
        )
        exhibitor_item.add_value("website", SelectJmes("[].url")(response_json))
        exhibitor_item.add_value("email", SelectJmes("[].email")(response_json))
        exhibitor_item.add_value("phone", SelectJmes("[].phone")(response_json))
        exhibitor_item.add_value("fax", SelectJmes("[].fax")(response_json))
        exhibitor_item.add_value("country", SelectJmes("[].country")(response_json))
        for key in ["state", "city", "address1"]:
            exhibitor_item.add_value("address", SelectJmes(f"[].{key}")(response_json))
        exhibitor_item.add_value(
            "description", SelectJmes("[].description")(response_json)
        )
        exhibitor_id = SelectJmes("[0].exhid")(response_json)
        yield response.follow(
            url=(
                self.EXHIBITOR_BOOTHS_API.format(exhibitor_id=exhibitor_id)
                if self.EXHIBITOR_BOOTHS_API
                else DEFAULT_EXHIBITOR_BOOTHS_API.format(
                    exhibitor_id=exhibitor_id,
                    exhibition_code=self.EXHIBITION_CODE,
                )
            ),
            callback=self.parse_exhibitor_booths,
            headers=self.HEADERS,
            meta={"exhibitor_item": exhibitor_item},
        )

    @staticmethod
    def parse_exhibitor_booths(response: TextResponse):
        exhibitor_item = response.meta["exhibitor_item"]
        response_json = response.json()
        exhibitor_item.add_value(
            "booth_number", SelectJmes("[].boothdisplay")(response_json)
        )
        exhibitor_item.add_value(
            "hall_location", SelectJmes("[].halldisplay")(response_json)
        )
        yield exhibitor_item.load_item()
