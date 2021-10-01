import datetime
import json
import urllib

from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse, JsonRequest

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.utils.wrappers import json_response_wrapper


class NeoconHubSpider(BaseSpider):
    name = "NeoconHubSpider"

    EXHIBITION_DATE = datetime.date(2021, 10, 4)
    EXHIBITION_NAME = "NeoCon 2021"
    EXHIBITION_WEBSITE = "https://neocon.com//"

    HEADERS = {
        "Host": "neoconoct21.onlineeventapi.com",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
        "Origin": "https://www.neoconhub.com",
        "Referer": "https://www.neoconhub.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5"
    }

    AUTHENTICATE_URL = "https://neoconoct21.onlineeventapi.com/authenticate"
    EXHIBITORS_URL = "https://neoconoct21.onlineeventapi.com/exhibitors"

    APP_CLIENT_ID = "s519bbrhd92n2kursua6vr07b"
    APP_CLIENT_SECRET = "1tlie714fqu2n9fdqv6u80tbot118p3mq81ofkpnir2p8bedgdbi"

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        AUTHENTICATE_URL,
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        request_body = {"app_client_id": self.APP_CLIENT_ID, "app_client_secret": self.APP_CLIENT_SECRET}
        # print(f"`{request_body}`", len(request_body))
        for url in self.URLS:
            yield JsonRequest(
                url,
                method="POST",
                data=request_body,
                headers={
                    **self.HEADERS,
                },
                callback=self.fetch_token,
            )

    def fetch_token(self, response: TextResponse):
        response_json = response.json()
        token_type = response_json.get("token_type")
        access_token = response_json.get("access_token")
        yield response.follow(
            self.EXHIBITORS_URL,
            callback=self.fetch_exhibitors,
            headers={**self.HEADERS, "x-oep-auth": f"{token_type} {access_token}"},
            meta={'handle_httpstatus_list': [303]}
        )

    def fetch_exhibitors(self, response: TextResponse):
        if response.status == 303:
            redirect_location = response.headers.get("location", "").decode()
            yield response.follow(
                redirect_location,
                callback=self.parse_exhibitors,
                meta=response.meta
            )
        else:
            yield self.parse_exhibitors(response)

    def parse_exhibitors(self, response: TextResponse):
        response_json = response.json()
        for exhibitor_json in response_json:
            item = self.item_loader(item=self.item(), response=response)
            item.add_value("exhibitor_name", exhibitor_json.get("exhibitor_name"))
            item.add_value("booth_number", SelectJmes("custom_attributes.Field4")(exhibitor_json))
            item.add_value("hall_location", SelectJmes("custom_attributes.Field3")(exhibitor_json))
            item.add_value(
                "address",
                SelectJmes(
                    "company_info.address.[state_province, postal_code, address_line_one, address_line_two, address_line_three][]"
                )(exhibitor_json)
            )
            item.add_value("country", SelectJmes("company_info.address.country")(exhibitor_json))
            item.add_value("category", SelectJmes("industry_category")(exhibitor_json))
            item.add_value("description", SelectJmes("exhibitor_description")(exhibitor_json))

            item.add_value("website", SelectJmes("company_info.website_url")(exhibitor_json))
            item.add_value("email", SelectJmes("contacts[].email")(exhibitor_json))
            item.add_value("phone", SelectJmes("company_info.[phone_number, mobile_number][]")(exhibitor_json))
            item.add_value("fax", SelectJmes("company_info.fax_number")(exhibitor_json))

            yield item.load_item()
