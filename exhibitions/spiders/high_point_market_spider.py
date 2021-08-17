import datetime

from scrapy.http import Response

from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.item_loaders.high_point_market_loader import HighPointMarketLoader
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class HighPointMarketSpider(BaseSpider):
    name = "HighPointMarketSpider"

    EXHIBITION_DATE = datetime.date(2021, 10, 16)
    EXHIBITION_NAME = "High Point Market - Fall"
    EXHIBITION_WEBSITE = "https://www.highpointmarket.org/"

    HEADERS = {}  # replace with headers dict

    item_loader = HighPointMarketLoader  # create new and replace with class name

    URLS = [
        "https://www.highpointmarket.org/exhibitor",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath('//div[@class="exhibitor-row"]/a[contains(@id, "lnkExhibitor")]/@href')
        yield from response.follow_all(exhibitors, callback=self.parse_exhibitors)

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(item=ExhibitorItem(), response=response)
        exhibitor_item.add_xpath("exhibitor_name", '//*[@id="ctl00_ContentPlaceHolder1_lblName"]//text()')
        exhibitor_item.add_xpath("website", '//*[@id="ctl00_ContentPlaceHolder1_lnkWebsite"]//text()')
        phone = response.xpath('//*[@id="exh-corpphone"]//text()').re_first(r"Corporate Phone:\s(.+)")
        exhibitor_item.add_value("phone", phone)
        exhibitor_item.add_xpath("booth_number", '//*[@id="exh-showroom"]/span/text()')
        neighborhood = response.xpath('//*[@id="exh-neighborhood"]//text()').re_first(r"Neighborhood:\s(.+)")
        exhibitor_item.add_value("hall_location", neighborhood)
        exhibitor_item.add_xpath("hall_location", '//*[@id="exh-shuttle"]//text()')
        exhibitor_item.add_xpath("description", '//*[@id="ctl00_ContentPlaceHolder1_lblDescription"]//text()')
        yield exhibitor_item.load_item()
