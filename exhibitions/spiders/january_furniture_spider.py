import datetime
import json

import scrapy
from scrapy.http import Response, TextResponse
from scrapy.utils.python import to_bytes

from exhibitions.constants import PROXY_ZYTE
from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class JanuaryFurnitureSpider(BaseSpider):
    name = "JanuaryFurnitureSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 23)
    EXHIBITION_NAME = "January Furniture Show"
    EXHIBITION_WEBSITE = "https://januaryfurnitureshow.com"

    HEADERS = {
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Sec-GPC": 1,
        "Host": "januaryfurnitureshow.com",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Origin": "https://januaryfurnitureshow.com",
        "Referer": "https://januaryfurnitureshow.com/search/exhibitors?"
    }

    item_loader = BaseItemLoader
    item = ExhibitorItem

    current_page: int = 0

    URLS = [
        "https://januaryfurnitureshow.com/search/exhibitors",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    @staticmethod
    def get_post_data(page_number: int) -> dict:
        return {
            "page": str(page_number),
            "qWhich": "exhibitors",
            "sTab": "all",
            "sort": "name",
            "q": "",
            "qFromPage": "",
            "letter": 0,
            "descr": "auto",
            "hall": "",
            "ecats": "",
            "cfilters": "",
            "tag": "",
            "country": "",
            "bcat": "",
            "business_area": "",
            "activity": "",
            "isnew": "off",
            "productLaunch": "off",
            "grid": 4
        }

    def start_requests(self):
        post_data = self.get_post_data(1)
        print(len(json.dumps(post_data)))
        for url in self.URLS:
            yield scrapy.FormRequest(
                url=url,
                formdata=post_data,
                headers=self.HEADERS,
                callback=self.fetch_exhibitors
            )

    def fetch_exhibitors(self, response: TextResponse):
        with open("dnt.html", "w") as f:
            f.write(response.text)
        response_json = response.json()
        result = response_json.get("result")
        pages = response_json.get("pages")
        if pages <= self.current_page:
            selector = scrapy.Selector(text=result, type="html")
            exhibitors = selector.xpath("//a[contains(@class, 'exhcard__img-link')]/@href").getall()
            for exhibitor_url in exhibitors:
                yield scrapy.Request(
                    url=exhibitor_url,
                    callback=self.parse_exhibitors
                )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(self.item(), response)
        exhibitor_item.add_xpath("exhibitor_name", "//*[@class='expo-container']//*[@class='prodmodal__info-title']")
        exhibitor_item.add_xpath("country", "//*[@class='expo-container']//*[@class='prodmodal__info-location']")
        exhibitor_item.add_xpath(
            "hall_location",
            "//*[@class='expo-container']//*[@class='prodmodal__info-details-item prodmodal__info-details-item_hall-stand']/span[contains(text(), 'Hall')]//following-sibling::*[1]"
        )
        exhibitor_item.add_xpath(
            "booth_number",
            "//*[@class='expo-container']//*[@class='prodmodal__info-details-item prodmodal__info-details-item_hall-stand']/span[contains(text(), 'Stand')]//following-sibling::*[1]"
        )
        exhibitor_item.add_xpath(
            "website",
            "//*[@class='expo-container']//*[@class='prodmodal__info-site']/a/@href"
        )
        yield exhibitor_item.load_item()
