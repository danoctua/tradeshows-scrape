import datetime

from scrapy import Selector
from scrapy.http import TextResponse

from exhibitions.item_loaders.feria_del_mueble_item_loader import (
    FeriaDelMuebleItemLoader,
)
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class FeriaDelMuebleSpider(BaseSpider):
    name = "FeriaDelMuebleSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 22)
    EXHIBITION_NAME = "Feria Del Mueble"
    EXHIBITION_WEBSITE = "https://www.feriazaragoza.com/feria-del-mueble-2022"

    HEADERS = {}  # replace with headers dict

    item_loader = FeriaDelMuebleItemLoader
    item = ExhibitorItem

    current_page = 1  # first landing page; don't use pagination as it's broken

    BASE_EXHIBITORS_LIST_URL = "https://www.feriazaragoza.com/feria-del-mueble-2022/visitors/list-of-exhibitors"

    URLS = [BASE_EXHIBITORS_LIST_URL]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def _get_exhibitors_list_url(self):
        self.current_page += 1
        return f"{self.BASE_EXHIBITORS_LIST_URL}?page={self.current_page}"

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath(
            "//div[@class='seccionExpositores table-responsive']/table/tbody/tr"
        )
        if exhibitors:
            for exhibitor in exhibitors:
                yield self.parse_exhibitor(response, exhibitor)

            if self.current_page < 6:
                yield response.follow(
                    url=self._get_exhibitors_list_url(),
                    callback=self.fetch_exhibitors,
                    headers=self.HEADERS,
                )

    def parse_exhibitor(self, response: TextResponse, selector: Selector):
        exhibitor_item = self.item_loader(self.item(), response=response)
        print(selector)
        _, name, stands, url = selector.xpath("./td")
        hall_location, booth_number = (
            stands.xpath(".//text()").get().split("-", maxsplit=1)
        )
        exhibitor_item.add_value("exhibitor_name", name.xpath(".//text()").get())
        exhibitor_item.add_value("hall_location", hall_location)
        exhibitor_item.add_value("booth_number", booth_number)
        exhibitor_item.add_value("website", url.xpath(".//text()").getall())
        return exhibitor_item.load_item()
