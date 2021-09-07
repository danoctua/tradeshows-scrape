import datetime
import json

from itemloaders.processors import SelectJmes
import scrapy
from scrapy.http import Response

from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


class InterGiftSpider(BaseSpider):
    name = "InterGiftSpider"

    EXHIBITION_DATE = datetime.date(2021, 9, 15)
    EXHIBITION_NAME = "Intergift- September"
    EXHIBITION_WEBSITE = "https://www.ifema.es/en/intergift"

    HEADERS = {
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Host": "api.swapcard.com",
        "Referer": "https://liveconnect.ifema.es/",
    }

    item_loader = BaseItemLoader

    BODY_PAYLOAD = {
        "operationName": "EventExhibitorList",
        "variables": {
            "viewId": "RXZlbnRWaWV3XzE2ODI4Mg==",
            "search": "",
            "selectedFilters": [{"mustEventFiltersIn": []}],
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "ee232939a5b943c0d87a4877655179bc2e5c73472ff99814119deddb34e0a3b6",
            }
        },
    }

    EXHIBITOR_INFO_PAYLOAD = {
        "operationName": "ExhibitorDetailsPageQuery",
        "variables": {
            "maxMembersToFetch": 100,
            "exhibitorId": None,
            "eventId": "RXZlbnRfMzc1OTc4",
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "093a75c3786f4468a2b3b264b2c4ba00ccfa094f8b972db8ecf71cb8d2cf91ed",
            }
        },
    }

    URLS = [
        "https://api.swapcard.com/graphql",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        for url in self.URLS:
            yield scrapy.Request(
                url=url,
                method="POST",
                body=json.dumps([self.BODY_PAYLOAD]),
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: dict):
        exhibitors = SelectJmes("[0].data.view.exhibitors.nodes")(response_json)
        for exhibitor in exhibitors:
            payload = self.EXHIBITOR_INFO_PAYLOAD.copy()
            payload["variables"]["exhibitorId"] = exhibitor["id"]
            yield response.follow(
                url=response.url,
                method="POST",
                body=json.dumps([payload]),
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
            )
            del payload
        if SelectJmes("[0].data.view.exhibitors.pageInfo.hasNextPage")(response_json):
            end_cursor = SelectJmes("[0].data.view.exhibitors.pageInfo.endCursor")(
                response_json
            )
            payload = self.BODY_PAYLOAD.copy()
            payload["variables"]["endCursor"] = end_cursor
            yield response.follow(
                url=response.url,
                method="POST",
                body=json.dumps([payload]),
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )
            del payload

    @json_response_wrapper
    def parse_exhibitors(self, response: Response, response_json: dict):
        exhibitor = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_json = SelectJmes("[0].data.exhibitor")(response_json)
        exhibitor.add_value("exhibitor_name", SelectJmes("name")(exhibitor_json))
        exhibitor.add_value("booth_number", SelectJmes("booth")(exhibitor_json))
        exhibitor.add_value(
            "address", SelectJmes("address.[state, street, zipCode]")(exhibitor_json)
        )
        exhibitor.add_value("country", SelectJmes("address.country")(exhibitor_json))
        exhibitor.add_value(
            "category",
            SelectJmes("[0].data.productCategories[].category.name")(response_json),
        )
        exhibitor.add_value("description", SelectJmes("description")(exhibitor_json))
        exhibitor.add_value("website", SelectJmes("websiteUrl")(exhibitor_json))
        exhibitor.add_value(
            "phone", SelectJmes("phoneNumbers[0].formattedNumber")(exhibitor_json)
        )
        exhibitor.add_value("email", SelectJmes("email")(exhibitor_json))
        return exhibitor.load_item()
