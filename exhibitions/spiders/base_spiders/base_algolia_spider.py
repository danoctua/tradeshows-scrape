import datetime
import json
from typing import Dict, Optional
from urllib.parse import urlencode

import scrapy
from itemloaders.processors import SelectJmes
from scrapy import Request
from scrapy.http import Response, TextResponse

from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


class BaseAlgoliaSpider(BaseSpider):

    HEADERS = {}  # replace with headers dict
    item_loader = BaseItemLoader  # create new and replace with class name

    URLS = []

    FORM_POST_BODY = """{{"params": "page={page}"}}"""

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    START_PAGE = 0
    HITS_PER_PAGE = 100

    PAYLOAD_BODY_PARAMS = {
        "query": "",
        "hitsPerPage": str(HITS_PER_PAGE),
        "maxValuesPerFacet": "1000",
        "page": None,  # has to be filled dynamically
        "highlightPreTag": "__ais-highlight__",
        "highlightPostTag": "__/ais-highlight__",
        "distinct": "true",
        "facetingAfterDistinct": "true",
        "facets": '["sector","exhibitor.country_en","label_en","h_categories.en.0"]',
        "tagFilters": "",
    }

    MAIN_RESPONSE_BODY_LOCATOR = ""

    def start_requests(self):
        for url in self.URLS:
            yield scrapy.Request(
                url=url,
                method="POST",
                body=self._get_payload_body(),
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

    def _get_payload_body(self, page: Optional[int] = None) -> str:
        """Method to get encoded payload body"""
        if page is None:
            page = self.START_PAGE

        payload_body_params = self.PAYLOAD_BODY_PARAMS.copy()
        payload_body_params["page"] = str(page)
        payload_body: dict = {
            "requests": [
                {
                    "indexName": "InsertionProduct_hall_desc",
                    "params": urlencode(payload_body_params),
                }
            ]
        }
        return json.dumps(payload_body)

    def fetch_exhibitors(self, response: TextResponse):
        response_json = response.json()
        if self.MAIN_RESPONSE_BODY_LOCATOR:
            response_json = SelectJmes(self.MAIN_RESPONSE_BODY_LOCATOR)(response_json)

        exhibitors = SelectJmes("hits[]")(response_json)
        for exhibitor in exhibitors:
            print(exhibitor)
            yield self.parse_exhibitor(response, exhibitor)
        page = response_json.get("page")
        # if page < response_json.get("nbPages"):
        #     yield scrapy.Request(
        #         url=response.url,
        #         method="POST",
        #         body=self._get_payload_body(page + 1),
        #         headers=self.HEADERS,
        #         callback=self.fetch_exhibitors,
        #     )

    def parse_exhibitor(self, response: TextResponse, exhibitor_info: Dict):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
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
