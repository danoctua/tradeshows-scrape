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

EXHIBITOR_INFO_API = "https://www.atlantamarket.com/imc-api/v2/exhibitors/OpenDetails?sc_apikey={API_KEY}&exhibitorIds={exhibitor_id}"
MAX_NUMBER_OF_EXHIBITORS = 2000


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
        "Sec-Fetch-Mode": "cors",
    }

    item_loader = AtlantaGiftItemLoader

    URLS = [
        f"https://www.atlantamarket.com/imc-api/v2/exhibitors/search?"
        f"sc_apikey={API_KEY}&term=all&type=exhibitorline&page=1&pageSize={MAX_NUMBER_OF_EXHIBITORS}",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: json):
        exhibitors_number = response_json.get("count", 0)
        if exhibitors_number <= 0:
            raise NoExhibitorException()
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

        item.add_value(
            "exhibitor_name", SelectJmes("companyDetails.companyName")(item_json)
        )
        item.add_value(
            "booth_number",
            SelectJmes("companyDetails.activeLeases[].showrooms[].showroom")(item_json),
        )
        item.add_value(
            "hall_location",
            SelectJmes(
                "companyDetails.activeLeases[].showrooms[].showroomBuildingName"
            )(item_json),
        )

        item.add_value(
            "address",
            [
                SelectJmes(f"directoryContactInfo.address{i}")(item_json)
                for i in range(1, 3)
            ],
        )
        countries = SelectJmes("directoryContactInfo.countries[]")(item_json)
        country_code = SelectJmes("directoryContactInfo.country")(item_json)
        try:
            country_code = int(country_code)
            item.add_value(
                "country",
                [
                    country["displayValue"]
                    for country in countries
                    if country["code"] == country_code
                ],
            )
        except (ValueError, TypeError):
            pass

        item.add_value(
            "category", SelectJmes("productCategories[].category.name")(item_json)
        )
        item.add_value(
            "description",
            SelectJmes("companyInformation.completeDescription")(item_json),
        )
        item.add_value(
            "website", SelectJmes("companyInformation.companyWebsiteUrl")(item_json)
        )
        item.add_value(
            "email",
            [
                SelectJmes(f"directoryContactInfo.companyEmail{i}")(item_json)
                for i in range(1, 3)
            ],
        )
        item.add_value(
            "phone",
            [
                SelectJmes(f"directoryContactInfo.primaryPhone{part}")(item_json)
                for part in ["Code", "No"]
            ],
        )
        item.add_value(
            "fax",
            [
                SelectJmes(f"directoryContactInfo.faxNumber{part}")(item_json)
                for part in ["Code", ""]
            ],
        )

        yield item.load_item()
