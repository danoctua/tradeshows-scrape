from typing import Dict, List

import datetime

from scrapy.http import Response

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper

EXHIBITOR_INFO_API = (
    "https://lf2021.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorInfo&exhID={exhibitor_id}"
)
EXHIBITOR_BOOTHS_API = (
    "https://lf2021.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorBooths&exhID={exhibitor_id}"
)


class LightFairSpider(BaseSpider):
    name = "LightFairSpider"

    EXHIBITION_DATE = datetime.date(2021, 10, 27)
    EXHIBITION_NAME = "Lightfair"
    EXHIBITION_WEBSITE = "https://www.lightfair.com/"

    HEADERS = {
        "X-Requested-With": "XMLHttpRequest"
    }  # replace with headers dict

    item_loader = BaseItemLoader  # create new and replace with class name

    URLS = [
        "https://lf2021.mapyourshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorNames",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: List[Dict]):
        for exhibitor_data in response_json:
            exhibitor_id = exhibitor_data.get("fieldvalue")
            if exhibitor_id:
                yield response.follow(
                    EXHIBITOR_INFO_API.format(exhibitor_id=exhibitor_id),
                    callback=self.parse_exhibitors,
                    headers=self.HEADERS
                )

    @json_response_wrapper
    def parse_exhibitors(self, response: Response, response_json: List[Dict]):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_info = response_json[0]
        exhibitor_item.add_value("exhibitor_name", exhibitor_info.get("exhname"))
        exhibitor_item.add_value("website", exhibitor_info.get("url"))
        exhibitor_item.add_value("email", exhibitor_info.get("email"))
        exhibitor_item.add_value("phone", exhibitor_info.get("phone"))
        exhibitor_item.add_value("fax", exhibitor_info.get("fax"))
        exhibitor_item.add_value("country", exhibitor_info.get("country"))
        for key in ["state", "city", "address1"]:
            exhibitor_item.add_value("address", exhibitor_info.get(key))
        exhibitor_item.add_value("description", exhibitor_info.get("description"))
        yield response.follow(
            EXHIBITOR_BOOTHS_API.format(exhibitor_id=exhibitor_info.get("exhid")),
            callback=self.parse_exhibitor_booths,
            headers=self.HEADERS,
            meta={"exhibitor_item": exhibitor_item}
        )

    @json_response_wrapper
    def parse_exhibitor_booths(self, response: Response, response_json: List[Dict]):
        exhibitor_item = response.meta["exhibitor_item"]
        exhibitor_info = response_json[0]
        exhibitor_item.add_value("booth_number", exhibitor_info.get("boothdisplay"))
        exhibitor_item.add_value("hall_location", exhibitor_info.get("halldisplay"))
        yield exhibitor_item.load_item()
