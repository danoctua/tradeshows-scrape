import datetime

from scrapy import FormRequest, Selector
from scrapy.http import TextResponse

from exhibitions.item_loaders.shkessen_item_loader import ShkessenItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class ShkessenSpider(BaseSpider):
    name = "ShkessenSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 8)
    EXHIBITION_NAME = "SHK"
    EXHIBITION_WEBSITE = "https://www.shkessen.de/sectoral-meeting-place/"

    HEADERS = {}  # replace with headers dict

    item_loader = ShkessenItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.shkessen.de/branchentreff/ausstellerliste/php_res/ajax-infinite-scroll.php?action=next_search_results&fair=E402&lang=en&page=1&type=json&csrf_token=QpAeNpsuTCn7%2FRa1UGUGQkX%2FscBhGZ%2BwYcp1bqVESIA%3D",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        html_response_raw = response.json().get("response")
        html_response_selector = Selector(text=html_response_raw, type="html")
        exhibitors = html_response_selector.xpath("//h2/a/@href").getall()
        for exhibitor in exhibitors:
            yield response.follow(url=exhibitor, callback=self.parse_exhibitors)
        next_url = response.json().get("next_data_url")
        if next_url:
            yield response.follow(next_url, callback=self.fetch_exhibitors)

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_item.add_xpath(
            "exhibitor_name", "//section[@id='zeile_aussteller_head']//h2/text()"
        )
        exhibitor_item.add_xpath(
            "country",
            "//section[@id='zeile_aussteller_head']//div[@class='tag']/a/text()",
        )
        exhibitor_item.add_xpath("address", "//address/text()")
        exhibitor_item.add_xpath(
            "website",
            "//section[@id='zeile_aussteller_infoblock']//a[@title='Homepage']/@href",
        )
        exhibitor_item.add_xpath(
            "phone",
            "//section[@id='zeile_aussteller_infoblock']//li[contains(./i/@class, 'fa-phone')]/text()",
        )
        exhibitor_item.add_xpath(
            "fax",
            "//section[@id='zeile_aussteller_infoblock']//li[contains(./i/@class, 'fa-fax')]/text()",
        )
        exhibitor_item.add_xpath(
            "email",
            "//section[@id='zeile_aussteller_infoblock']//a[@title='E-mail']/@href",
        )

        booths = response.xpath(
            "//section[@id='zeile_aussteller_head']//div[@class='tag_stand']"
        )
        for booth in booths:
            child_exhibitor_item = self.item_loader(
                item=self.item(exhibitor_item.load_item()), response=response
            )
            child_exhibitor_item.add_value(
                "hall_location", booth.xpath("./a/text()").get()
            )
            child_exhibitor_item.add_value(
                "booth_number", booth.xpath("./span/text()").get()
            )
            yield child_exhibitor_item.load_item()
