import scrapy
from typing import Dict, List, Optional, Union

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem


class BaseSpider(scrapy.Spider):

    name: str  # name of the spider
    URLS: List[str]  # list of initial urls - to be defined in the spider
    HEADERS: Dict[str, Union[str, int, bool]] = {}  # request headers

    ONLY_FIELDS: Optional[tuple] = None  # fields to export

    item_loader = BaseItemLoader
    item = ExhibitorItem

    def start_requests(self):
        for url in self.URLS:
            yield scrapy.Request(
                url=url, headers=self.HEADERS, callback=self.fetch_exhibitors
            )

    def parse(self, response, **kwargs):
        # not using, but needed to implement all abstract methods
        pass

    def fetch_exhibitors(self, response):
        raise NotImplementedError

    def parse_exhibitors(self, response):
        raise NotImplementedError
