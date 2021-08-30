import datetime

from itemloaders.processors import SelectJmes
from scrapy.http import Response, Request

from exhibitions.item_loaders.salone_milano_loader import SaloneMilanoItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


API_SPIDER_FIELDS_MAPPING = (
    ("nomeEspositore", "exhibitor_name"),
    ("indirizzo", "comune", "provinciaNome", "address"),
    ("nazioneIso3AlphaCode", "country"),
    ("telefono", "phone"),
    ("fax", "fax"),
    ("email", "email"),
    ("sitoInternet", "website"),
    ("marchiDescrizione", "description"),
    (("categorieI", "categorieE"), "category"),
    ("stand", "booth_number"),
    ("hall", "hall_location")
)


class SaloneMilanoApiSpider(BaseSpider):
    """This spider is not fully functioning - headers has to be adjusted to send request
    and following requests has to be made.
    """
    name = "SaloneMilanoApiSpider"

    EXHIBITION_DATE = datetime.date(2021, 5, 9)
    EXHIBITION_NAME = "Salone del Mobile 2021"
    EXHIBITION_WEBSITE = "https://salonemilano.it/"

    HEADERS = {
        "Content-Type": "application/json; charset=UTF-8",
        "Host": "hzh2dgp2ke.execute-api.eu-west-1.amazonaws.com"
    }  # replace with headers dict

    item_loader = SaloneMilanoItemLoader

    PAGE_SIZE = 200  # max available
    INITIAL_PAGE_NUMBER = 1

    API_URL = "https://hzh2dgp2ke.execute-api.eu-west-1.amazonaws.com/main/exhibitorSearch"

    URLS = [API_URL]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def get_request_url(self, page_number):
        request_body = str(
            {"params": f"anno={self.EXHIBITION_DATE.year}&pageSize={self.PAGE_SIZE}&pageNumber={page_number}"}
        )
        return Request(
            method="POST",
            url=self.API_URL,
            body=request_body,
            headers={**self.HEADERS, "Content-Length": len(request_body)},
            callback=self.fetch_exhibitors
        )

    def start_requests(self):
        request = self.get_request_url(self.INITIAL_PAGE_NUMBER)
        print(request.body, len(request.body))
        yield self.get_request_url(self.INITIAL_PAGE_NUMBER)

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: dict):
        data = response_json.get("data") or []
        for exhibitor in data[:5]:
            self.parse_exhibitor(exhibitor, response=response)

    def parse_exhibitor(self, exhibitor: dict, response: Response):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        for *api_fields, item_field in API_SPIDER_FIELDS_MAPPING:
            exhibitor_item.add_value(item_field, SelectJmes(f"[{', '.join(api_fields)}]")(exhibitor))
        # replace with method parse exhibitors data
        yield exhibitor_item.load_item()
