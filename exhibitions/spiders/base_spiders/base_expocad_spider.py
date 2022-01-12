import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional

from scrapy import Selector
from scrapy.http import Response

from exhibitions.spiders.base_spiders.base_spider import BaseSpider
from exhibitions.item_loaders.base_item_loaders.base_expocad_item_loader import (
    BaseExpocadItemLoader,
)


@dataclass
class ExhibitorDTO:
    name: str
    booth_number: str

    def __init__(self, names: list[str], booth_number: str) -> None:
        self.name = " ".join(names)
        self.booth_number = booth_number


class BaseExpocadSpider(BaseSpider):
    name = "BaseExpocadSpider"

    item_loader = BaseExpocadItemLoader

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        },
    }

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
    }

    URLS = []

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath("//SS/S")
        exhibitors_not_filtered = (
            self.parse_exhibitor(exhibitor) for exhibitor in exhibitors
        )
        exhibitors_booths = defaultdict(list)
        for exhibitor in (
            exhibitor for exhibitor in exhibitors_not_filtered if exhibitor
        ):
            exhibitors_booths[exhibitor.name].append(exhibitor.booth_number)

        for exhibitor_name, exhibitor_booths in exhibitors_booths.items():
            exhibitor_item = self.item_loader(item=self.item(), response=response)
            exhibitor_item.add_value("exhibitor_name", exhibitor_name)
            exhibitor_item.add_value("booth_number", exhibitor_booths)
            yield exhibitor_item.load_item()

    @staticmethod
    def parse_exhibitor(selector: Selector) -> Optional[ExhibitorDTO]:
        exhibitor_data: list = selector.xpath("./T[@t='0']/@v").getall()
        # print(selector, exhibitor_data)
        if exhibitor_data:
            booth_number, *exhibitor_names = exhibitor_data
            return ExhibitorDTO(names=exhibitor_names, booth_number=booth_number)
