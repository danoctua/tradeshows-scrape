import scrapy
from typing import List, Optional
import abc


class BaseSpider(scrapy.Spider):
    name: str  # name of the spider
    URLS: List[str]  # list of initial urls - to be defined in the spider

    ONLY_FIELDS: Optional[tuple] = None  # fields to export

    def start_requests(self):
        for url in self.URLS:
            yield scrapy.Request(url=url, callback=self.fetch_exhibitors)

    @abc.abstractmethod
    def fetch_exhibitors(self, request):
        pass

    @abc.abstractmethod
    def parse_exhibitors(self, request):
        pass
