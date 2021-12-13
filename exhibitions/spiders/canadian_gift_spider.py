import datetime

import scrapy
from itemloaders.processors import SelectJmes
from scrapy.http import TextResponse

from exhibitions.item_loaders.canadian_gift_item_loader import CanadianGiftItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class CanadianGiftSpider(BaseSpider):
    name = "CanadianGiftSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 30)
    EXHIBITION_NAME = "Toronto Gift - Spring"
    EXHIBITION_WEBSITE = "https://www.cangift.org/toronto-gift-fair/en/home/"

    HEADERS = {
        "Host": "ecw.cangift.org",
        "Content-Length": 2,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "DNT": 1,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "http://ecw.cangift.org",
        "Referer": "http://ecw.cangift.org/ecw_TR/ec/forms/attendee/index5.aspx?searchText=%20&content=list&lang=en&PLshows=TR",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,pl-PL;q=0.6,pl;q=0.5",
    }

    item_loader = CanadianGiftItemLoader
    item = ExhibitorItem

    LIST_API_URL: str = (
        "http://ecw.cangift.org/ecw_TR/Integration/EC/JsonService.asmx/GetPackage2"
    )
    EXHIBITOR_API_URL: str = (
        "http://ecw.cangift.org/ecw_TR/ec/forms/attendee/vbooth5.aspx?id={exhibitor_id}"
    )

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.LIST_API_URL,
            method="POST",
            body="{}",
            callback=self.fetch_exhibitors,
            headers=self.HEADERS,
        )

    def fetch_exhibitors(self, response: TextResponse):
        response_json = response.json()
        exhibitors_data: list = SelectJmes("d.e")(response_json)
        exhibitor_ids = [exhibitor_data[0] for exhibitor_data in exhibitors_data]
        for exhibitor_id in exhibitor_ids:
            yield response.follow(
                url=self.EXHIBITOR_API_URL.format(exhibitor_id=exhibitor_id),
                callback=self.parse_exhibitors,
            )

    def parse_exhibitors(self, response: TextResponse):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath("exhibitor_name", "//span[@id='lblName']/text()")
        exhibitor_item.add_xpath("booth_number", "//a[@id='boothsLink']/text()")
        exhibitor_item.add_xpath(
            "phone",
            "//span[contains(@id, 'lblvbBCardAddr') and contains(text(), 'Phone')]/text()",
        )
        exhibitor_item.add_xpath(
            "phone",
            "//span[contains(@id, 'lblvbBCardAddr') and contains(text(), 'Fax')]/text()",
        )
        exhibitor_item.add_xpath("website", "//a[@id='linkvbBCardUrl']/text()")
        exhibitor_item.add_xpath("description", "//span[@id='lblvbProfile']/p/text()")
        exhibitor_item.add_xpath("category", "//span[@id='lblvbCats']/td/text()")
        exhibitor_item.add_xpath("brands", "//li[contains(@id, 'vbBrandItem')]/text()")
        return exhibitor_item.load_item()
