import datetime
from urllib.parse import urlencode

from itemloaders.processors import SelectJmes
from scrapy import Request

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class HeimTextilSpider(BaseSpider):
    name = "HeimTextilSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 13)
    EXHIBITION_NAME = "heimtextil"
    EXHIBITION_WEBSITE = "https://heimtextil.messefrankfurt.com"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    HITS_PER_PAGE: int = 200
    INITIAL_PAGE_NUM: int = 1

    QUERY_PARAMS = {
        "language": "en-GB",
        "q": "",
        "orderBy": "name",
        "pageNumber": INITIAL_PAGE_NUM,
        "pageSize": HITS_PER_PAGE,
        "showJumpLabels": False,
        "findEventVariable": "HEIMTEXTIL",
    }

    EXHIBITOR_SEARCH_URL: str = (
        "https://exhibitorsearch.messefrankfurt.com/service/esb/2.1/search/exhibitor"
    )

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        yield Request(
            url=f"{self.EXHIBITOR_SEARCH_URL}?{urlencode(self.QUERY_PARAMS)}",
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
        print(
            "CURRENT PAGE",
            current_page,
            hits_total,
            SelectJmes("result.metaData")(response_json),
        )

        if current_page < hits_total:
            query_params = self.QUERY_PARAMS.copy()
            query_params["pageNumber"] = (
                current_page // self.HITS_PER_PAGE + 2
            )  # 1) add first page 2) add next page
            print(query_params)
            yield response.follow(
                url=f"{self.EXHIBITOR_SEARCH_URL}?{urlencode(query_params)}",
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
            "address", SelectJmes("address.country.[zip, city, street]")(exhibitor)
        )
        exhibitor_item.add_value("category", SelectJmes("categories[].name")(exhibitor))
        exhibitor_item.add_value(
            "description", SelectJmes("description.text")(exhibitor)
        )
        exhibitor_item.add_value("website", SelectJmes("homepage")(exhibitor))
        exhibitor_item.add_value("email", SelectJmes("contacts[].email")(exhibitor))
        exhibitor_item.add_value("phone", SelectJmes("contacts[].phone")(exhibitor))
        return exhibitor_item.load_item()
