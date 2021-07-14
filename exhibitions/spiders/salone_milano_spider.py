import datetime

from scrapy.http import Response

from exhibitions.spiders.base_spider import BaseSpider
from exhibitions.item_loaders.salone_milano_loader import SaloneMilanoItemLoader
from exhibitions.items.exhibitor import ExhibitorItem


class SaloneMilanoSpider(BaseSpider):
    name = "SaloneMilanoSpider"

    EXHIBITION_DATE = datetime.date(2021, 5, 9)
    EXHIBITION_NAME = "Salone del Mobile 2021"
    EXHIBITION_WEBSITE = "https://salonemilano.it/"

    EXHIBITOR_FETCH_START_LINK = "https://www.salonemilano.it/it/brand?title=&sort_by=title&page=0"

    HEADERS = {}  # replace with headers dict

    item_loader = SaloneMilanoItemLoader  # create new and replace with class name

    URLS = [
        EXHIBITOR_FETCH_START_LINK,
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath("//*[contains(@class, 'list-flex-element-brands')]/a")
        for exhibitor in exhibitors:
            yield response.follow(exhibitor, callback=self.parse_exhibitors)
        next_page = response.xpath("//*[contains(@class, 'pager__item')]/a/@href").get()
        if next_page:
            yield response.follow(f'{response.url.split("?")[0]}{next_page}', callback=self.fetch_exhibitors)

    def parse_exhibitors(self, response: Response):
        item_loader = self.item_loader(ExhibitorItem(), response=response)
        item_loader.add_xpath("exhibitor_name", "//h1[contains(@class, 'heading-1')]/text()")
        item_loader.add_xpath(
            "description",
            "//*[contains(@id, 'About')]//*[contains(@class, 'text-paragraph')][1]//text()"
        )
        yield item_loader.load_item()
