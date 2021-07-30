import datetime
import json
import warnings

from scrapy.http import Response
from itemloaders.processors import SelectJmes

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.atlanta_gift_item_loader import AtlantaGiftItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.utils.exceptions import NoExhibitorException
from exhibitions.utils.wrappers import json_response_wrapper

API_KEY = "391D75C6-01EE-463C-8B51-47B2748F8ACD"

EXHIBITOR_INFO_API = (
    "https://www.atlantamarket.com/imc-api/v2/exhibitors/OpenDetails?sc_apikey={API_KEY}&exhibitorIds={exhibitor_id}"
)
MAX_NUMBER_OF_EXHIBITORS = 2000

"""
GET /imc-api/v2/exhibitors/OpenDetails?sc_apikey=391D75C6-01EE-463C-8B51-47B2748F8ACD&exhibitorIds=108213&pageId=efe5561c-306f-4587-a2aa-b774c8f3dcaa& HTTP/1.1
Host: www.atlantamarket.com
Connection: keep-alive
sec-ch-ua: " Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"
DNT: 1
Channel: atlanta-market
sec-ch-ua-mobile: ?0
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36
Content-Type: application/json;charset=UTF-8
Accept: */*
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: cors
Sec-Fetch-Dest: empty
Referer: https://www.atlantamarket.com/exhibitor/108213/line/78632fb4-4cc7-915c-b64d-62f63e6ba93c
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5
Cookie: ASP.NET_SessionId=3afvslxlr2xpbhx3cqanwyey; sxa_site=atlanta-market; ai_user=BjvZR|2021-06-27T18:48:46.950Z; _gcl_au=1.1.1083267505.1624819728; _ga=GA1.2.447331850.1624819728; _gid=GA1.2.1298440627.1624819728; SC_ANALYTICS_GLOBAL_COOKIE=a1ebccddc21843f5957f2ed92e9e139f|True; _fbp=fb.1.1624819728280.1921458913; __qca=P0-1096066337-1624819728291; GDPRConsentCookieValue=gdpr-accepted; privacyPolicy=1; atlanta-market#lang=en; __RequestVerificationToken=Wx4YdFdhzBnHnD3JCHmb3vN30P1vGOt2ZV8RhpX-RB3N740bUGCR8aeV0vJN6YG34_C0EgQ1fkGTofLqauEiqVfRxbjwiqUMVHvxv44Ksdk1; _gat_UA-8853464-22=1; x-ms-routing-name=self; TiPMix=57.2307941304663; _gat_UA-8853464-20=1

"""


class AtlantaGiftSpider(BaseSpider):

    """
    JSON APi spider which fetches list of exhibitors from the API
    and later fetch their data from other API endpoint.
    """

    name = "AtlantaGiftSpider"

    EXHIBITION_DATE = datetime.date(2021, 7, 14)
    EXHIBITION_NAME = "Atlanta Gift - Summer"
    EXHIBITION_WEBSITE = "https://atlantamarket.com/"

    HEADERS = {
        "Channel": "atlanta-market",
        "Connection": "keep-alive",
        "Host": "www.atlantamarket.com",
        "Accept": "*/*",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors"
    }

    item_loader = AtlantaGiftItemLoader

    URLS = [
        f"https://www.atlantamarket.com/imc-api/v2/exhibitors/search?sc_apikey={API_KEY}&term=all&type=exhibitorline&page=1&pageSize={MAX_NUMBER_OF_EXHIBITORS}",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: json):
        exhibitors_number = response_json.get("count", 0)
        if exhibitors_number <= 0:
            raise NoExhibitorException
        if exhibitors_number > MAX_NUMBER_OF_EXHIBITORS:
            warnings.warn(f"The current list of exhibitors is longer, than you expect: {exhibitors_number} vs {MAX_NUMBER_OF_EXHIBITORS}")
        exhibitors_list = SelectJmes("data[].exhibitorId")(response_json)
        for exhibitor_id in exhibitors_list:
            yield response.follow(
                EXHIBITOR_INFO_API.format(API_KEY=API_KEY, exhibitor_id=exhibitor_id),
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
            )

    @json_response_wrapper
    def parse_exhibitors(self, response: Response, response_json: json):
        item_json = SelectJmes("data[0]")(response_json)
        if response_json.get("count", 0) <= 0 or not item_json:
            raise NoExhibitorException()

        item = self.item_loader(item=ExhibitorItem(), response=response)

        item.add_value("exhibitor_name", SelectJmes("companyDetails.companyName")(item_json))
        item.add_value("booth_number", SelectJmes("companyDetails.activeLeases[].showrooms[].showroom")(item_json))
        item.add_value("hall_location", SelectJmes("companyDetails.activeLeases[].showrooms[].showroomBuildingName")(item_json))

        item.add_value("address", [SelectJmes(f"directoryContactInfo.address{i}")(item_json) for i in range(1, 3)])
        countries = SelectJmes("directoryContactInfo.countries[]")(item_json)
        country_code = SelectJmes("directoryContactInfo.country")(item_json)
        try:
            country_code = int(country_code)
            item.add_value("country", [country["displayValue"] for country in countries if country["code"] == country_code])
        except (ValueError, TypeError):
            pass

        item.add_value("category", SelectJmes("productCategories[].category.name")(item_json))
        item.add_value("description", SelectJmes("companyInformation.completeDescription")(item_json))
        item.add_value("website", SelectJmes("companyInformation.companyWebsiteUrl")(item_json))
        item.add_value("email", [SelectJmes(f"directoryContactInfo.companyEmail{i}")(item_json) for i in range(1, 3)])
        item.add_value(
            "phone",
            [SelectJmes(f"directoryContactInfo.primaryPhone{part}")(item_json) for part in ["Code", "No"]]
        )
        item.add_value(
            "fax",
            [SelectJmes(f"directoryContactInfo.faxNumber{part}")(item_json) for part in ["Code", ""]]
        )

        yield item.load_item()
