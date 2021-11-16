import datetime
from typing import Dict, List

from scrapy.http import Response
from itemloaders.processors import SelectJmes

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.las_vegas_market_loader import LasVegasMarketItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.utils.wrappers import json_response_wrapper
from exhibitions.utils.request import RequestWithParams, parse_params
from exhibitions.utils.exceptions import NoExhibitorException


class LasVegasMarketSpider(BaseSpider):
    name = "LasVegasMarketSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 23)
    EXHIBITION_NAME = "Las Vegas Market - Winter"
    EXHIBITION_WEBSITE = "https://www.lasvegasmarket.com/"

    HEADERS = {
        "host": "www.lasvegasmarket.com",
        "channel": "las-vegas-market",
    }

    item_loader = LasVegasMarketItemLoader

    PAGE_SIZE = 12
    API_KEY = "391D75C6-01EE-463C-8B51-47B2748F8ACD"

    URLS = [
        f"https://www.lasvegasmarket.com/imc-api/v2/exhibitors/search?sc_apikey={API_KEY}&pageSize={PAGE_SIZE}",
    ]

    EXHIBITOR_DETAILS_API = f"https://www.lasvegasmarket.com/imc-api/v2/exhibitors/OpenDetails?sc_apikey={API_KEY}"

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    @json_response_wrapper
    def fetch_exhibitors(self, response: Response, response_json: dict):
        exhibitors = SelectJmes("data[].exhibitorId")(response_json)
        for exhibitor in set(exhibitors):
            yield RequestWithParams(
                url=self.EXHIBITOR_DETAILS_API,
                params={"exhibitorIds": exhibitor},
                callback=self.parse_exhibitors,
                headers=self.HEADERS,
                meta=response.meta,
            )

        current_page = int(parse_params(response.url).get("page", [1])[0])
        if exhibitors:
            yield RequestWithParams(
                url=response.url,
                params={"page": current_page + 1},
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

    @json_response_wrapper
    def parse_exhibitors(self, response: Response, response_json: dict):
        exhibitor_data = SelectJmes("data[0]")(response_json) or {}
        if not exhibitor_data:
            raise NoExhibitorException
        exhibitor_item = self.item_loader(item=ExhibitorItem())
        exhibitor_item.add_value(
            "exhibitor_name", SelectJmes("companyDetails.companyName")(exhibitor_data)
        )
        exhibitor_item.add_value(
            "website",
            SelectJmes("companyInformation.companyWebsiteUrl")(exhibitor_data),
        )
        exhibitor_item.add_value(
            "email",
            SelectJmes("directoryContactInfo.directoryContactEmail")(exhibitor_data),
        )
        exhibitor_item.add_value(
            "phone", SelectJmes("directoryContactInfo.primaryPhoneNo")(exhibitor_data)
        )
        exhibitor_item.add_value(
            "fax", SelectJmes("directoryContactInfo.faxNumber")(exhibitor_data)
        )
        exhibitor_item.add_value(
            "booth_number",
            SelectJmes("companyDetails.activeLeases[].showrooms[].showroom")(
                exhibitor_data
            ),
        )
        exhibitor_item.add_value(
            "hall_location",
            SelectJmes(
                "companyDetails.activeLeases[].showrooms[].showroomBuildingName"
            )(exhibitor_data),
        )
        countries = SelectJmes("directoryContactInfo.countries")(exhibitor_data)
        country_code = SelectJmes("directoryContactInfo.country")(exhibitor_data)
        country, state = self.get_country_name_by_code(country_code, countries)
        exhibitor_item.add_value("country", country)

        exhibitor_item.add_value("address", state)
        exhibitor_item.add_value(
            "address",
            SelectJmes("directoryContactInfo.[address1, address2, city]")(
                exhibitor_data
            ),
        )

        exhibitor_item.add_value(
            "category", SelectJmes("productCategories[].category.name")(exhibitor_data)
        )
        exhibitor_item.add_value(
            "description",
            SelectJmes("companyInformation.completeDescription")(exhibitor_data),
        )

        yield exhibitor_item.load_item()

    @staticmethod
    def get_country_name_by_code(country_code: str, countries: [List[Dict]]) -> tuple:
        country_code = int(country_code)
        for country in countries:
            if country.get("code") == country_code:
                states = country.get("state")
                country_state = None
                if isinstance(states, list):
                    for state in states:
                        if state.get("checked") == "1":
                            country_state = state.get("displayValue")
                return country.get("displayValue"), country_state

        return None, None
