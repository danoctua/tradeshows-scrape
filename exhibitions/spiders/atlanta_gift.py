import datetime
import json
from urllib.parse import urlencode

from scrapy import Request
from scrapy.http import Response
from itemloaders.processors import SelectJmes

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.atlanta_gift_item_loader import AtlantaGiftItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.utils.exceptions import NoExhibitorException
from exhibitions.utils.wrappers import json_response_wrapper

API_KEY = "391D75C6-01EE-463C-8B51-47B2748F8ACD"
SEARCH_PAGE = "b20c0e90-484d-4848-8ea6-bc3b2bcc391f"

EXHIBITOR_INFO_API = "https://www.atlantamarket.com/imc-api/v2/exhibitors/OpenDetails?sc_apikey={API_KEY}&exhibitorIds={exhibitor_id}"
MAX_NUMBER_OF_EXHIBITORS = 2000


class AtlantaGiftSpider(BaseSpider):

    """
    JSON APi spider which fetches list of exhibitors from the API
    and later fetch their data from other API endpoint.
    """

    name = "AtlantaGiftSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 11)
    EXHIBITION_NAME = "Atlanta Gift"
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

    QUERY_PARAMS = [
        {
            "sc_apikey": API_KEY,
            "page": 1,
            "pageSize": MAX_NUMBER_OF_EXHIBITORS,
            "searchPage": SEARCH_PAGE,
            "f:Product Categories": "256|257|259|37|148|135|149|150|151|152|139|147|145|36|243|244|245|246|247|253|251|34|236|237|238|240|33|264|267|228|278|231|325|229|230|29|372|375|377|302|385|389|390|391|393|396|28|374|373|378|379|380|300|304|388|392|394|397|398|15|211|212|362|216|356|370|359|364|354|355|361|371|367|366|360|357|219|218|368|369|27|194|197|198|196|199|200|202|24|265|266|174|285|179|288|291|292|320|332|336|22|203|270|204|205|206|185|207|208|209|328|210|21|401|340|303|188|189|190|339|338|19|346|290|324|295|347|315|345|165|316|400|329|335|403|16|402|9|92|93|94|279|280|95|84|293|97|98|99|101|103|104|105|106|12|108|109|141|142|134|136|137|91|143|144|112|10|83|23|258|268|120|121|122|123|126|127|128|130|5|406|75|6|51|20|59|30|32|26|73",
        },
        {
            "sc_apikey": API_KEY,
            "page": 1,
            "pageSize": MAX_NUMBER_OF_EXHIBITORS,
            "searchPage": SEARCH_PAGE,
            "f:Product Categories": "86|38",
        },
    ]

    EXHIBITORS_LIST_URL = "https://www.atlantamarket.com/imc-api/v2/exhibitors/search"

    URLS = []

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        for query_params in self.QUERY_PARAMS:
            yield Request(
                url=f"{self.EXHIBITORS_LIST_URL}?{urlencode(query_params)}",
                callback=self.fetch_exhibitors,
                headers=self.HEADERS,
            )

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
            )(item_json)
            or "",
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
                x
                for x in [
                    SelectJmes(f"directoryContactInfo.companyEmail{i}")(item_json)
                    for i in range(1, 3)
                ]
                if x
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
