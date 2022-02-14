import datetime

from scrapy import Selector
from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class InspiredHomeShowSpider(BaseSpider):
    name = "InspiredHomeShowSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 5)
    EXHIBITION_NAME = "International Housewares Association (IHA)"
    EXHIBITION_WEBSITE = "https://www.housewares.org/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://app.theinspiredhomeshow.com/Connect365/Results/ByBadge?BadgeId=18&activeFilterTypes=%5B%5D&activeFilterBadges=%5B%5D&activeFilterCategories=%5B%5D",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath(
            "//div[contains(@class, 'results-filterable-item')]"
        )
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(response, exhibitor)

    def parse_exhibitor(self, response: TextResponse, exhibitor: Selector):
        exhibitor_item = self.item_loader(self.item(), exhibitor)
        exhibitor_item.add_xpath("exhibitor_name", ".//h2/text()")
        exhibitor_item.add_xpath(
            "booth_number", ".//p[contains(text(), 'Booth Number')]/a/text()"
        )
        exhibitor_item.add_xpath(
            "description", ".//div[@class='result-description']//text()"
        )
        return exhibitor_item.load_item()
