import datetime
from urllib.parse import urlencode

from itemloaders.processors import SelectJmes
from scrapy import Request

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class BaseMesseFrankfurtSpider(BaseSpider):

    item_loader = BaseItemLoader
    item = ExhibitorItem

    HITS_PER_PAGE: int = 200
    INITIAL_PAGE_NUM: int = 1

    FIND_EVENT_VARIABLE: str
    EXHIBITOR_SEARCH_URL: str

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def get_query_params(self, page_number: int = None) -> dict:
        page_number = page_number or self.INITIAL_PAGE_NUM
        return {
            "language": "en-GB",
            "q": "",
            "orderBy": "name",
            "pageNumber": page_number,
            "pageSize": self.HITS_PER_PAGE,
            "showJumpLabels": False,
            "findEventVariable": self.FIND_EVENT_VARIABLE,
        }

    def start_requests(self):
        yield Request(
            url=f"{self.EXHIBITOR_SEARCH_URL}?{urlencode(self.get_query_params())}",
            callback=self.fetch_exhibitors,
            headers=self.HEADERS,
        )

    def fetch_exhibitors(self, response: TextResponse):
        response_json: dict = response.json()
        exhibitors = SelectJmes("result.hits[].exhibitor")(response_json)
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(response, exhibitor)

        current_page: int = SelectJmes("result.metaData.currentPage")(response_json)
        hits_total: int = SelectJmes("result.metaData.hitsTotal")(response_json)

        if current_page < hits_total:
            # 1) add first page 2) add next page
            next_page_number = current_page // self.HITS_PER_PAGE + 2
            yield response.follow(
                url=f"{self.EXHIBITOR_SEARCH_URL}?{urlencode(self.get_query_params(next_page_number))}",
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

    def parse_exhibitor(self, response: TextResponse, exhibitor: dict):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_value("exhibitor_name", SelectJmes("name")(exhibitor))
        exhibitor_item.add_value(
            "booth_number",
            SelectJmes("exhibition.exhibitionHall[].stand[].name")(exhibitor),
        )
        exhibitor_item.add_value(
            "hall_location", SelectJmes("exhibition.exhibitionHall[].name")(exhibitor)
        )
        exhibitor_item.add_value(
            "country", SelectJmes("address.country.label")(exhibitor)
        )
        exhibitor_item.add_value(
            "address", SelectJmes("address.[zip, city, street]")(exhibitor)
        )
        exhibitor_item.add_value("category", SelectJmes("categories[].name")(exhibitor))
        exhibitor_item.add_value(
            "description", SelectJmes("description.text")(exhibitor)
        )
        exhibitor_item.add_value("website", SelectJmes("homepage")(exhibitor))
        exhibitor_item.add_value("email", SelectJmes("contacts[].email")(exhibitor))
        exhibitor_item.add_value("phone", SelectJmes("contacts[].phone")(exhibitor))
        return exhibitor_item.load_item()
