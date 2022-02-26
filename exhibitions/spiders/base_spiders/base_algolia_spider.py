import datetime
import json
from typing import Dict

from itemloaders.processors import SelectJmes
from scrapy import Request
from scrapy.http import Response, TextResponse

from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


class BaseAlgoliaSpider(BaseSpider):
    item_loader = BaseItemLoader  # create new and replace with class name

    FORM_POST_BODY = """{{"params": "page={page}"}}"""

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    FROM_POST_BODY_JSON = {
        "requests": [
            {
                "indexName": "InsertionProduct_hall_desc",
                "params": "query=&hitsPerPage=24&maxValuesPerFacet=1000&page={}&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&distinct=true&facetingAfterDistinct=true&facets=%5B%22sector%22%2C%22exhibitor.country_en%22%2C%22label_en%22%2C%22h_categories.en.0%22%5D&tagFilters=",
            }
        ]
    }

    @staticmethod
    def _get_form_post_body(page: int) -> str:
        return json.dumps(
            {
                "requests": [
                    {
                        "indexName": "InsertionProduct_hall_desc",
                        "params": f"query=&hitsPerPage=24&maxValuesPerFacet=1000&page={page}&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&distinct=true&facetingAfterDistinct=true&facets=%5B%22sector%22%2C%22exhibitor.country_en%22%2C%22label_en%22%2C%22h_categories.en.0%22%5D&tagFilters=",
                    }
                ]
            },
            separators=(",", ":"),
        )

    def start_requests(self):
        for url in self.URLS:
            yield Request(
                url=url,
                method="POST",
                body=self._get_form_post_body(0),
                headers=self.HEADERS,
                callback=self.fetch_exhibitors,
            )

    def fetch_exhibitors(self, response: TextResponse):
        # print(response.text)
        response_json = SelectJmes("results[] | [0]")(response.json())
        exhibitors = SelectJmes("hits[]")(response_json)
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(response, exhibitor)
        page = response_json.get("page")
        if page < response_json.get("nbPages"):
            yield response.follow(
                url=response.url,
                method="POST",
                body=self._get_form_post_body(page + 1),
                headers=self.HEADERS,
                callback=self.fetch_exhibitors,
            )

    def parse_exhibitor(self, response: Response, exhibitor_info: Dict):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_item.add_value("exhibitor_name", exhibitor_info.get("name_en"))
        if not exhibitor_info.get("name_en"):
            return

        exhibitor_item.add_value(
            "brands", SelectJmes("brand.name.value")(exhibitor_info)
        )
        exhibitor_item.add_value(
            "category", SelectJmes("h_categories.en.*[]")(exhibitor_info)
        )
        exhibitor_item.add_value(
            "description",
            SelectJmes("description_en.value")(exhibitor_info)
            or exhibitor_info.get("web_catalog_description_en"),
        )
        exhibitor_item.add_value("hall_location", exhibitor_info.get("hall"))
        exhibitor_item.add_value("booth_number", exhibitor_info.get("stands"))
        exhibitor_item.add_value("country", exhibitor_info.get("exhibitor.country_en"))
        return exhibitor_item.load_item()
