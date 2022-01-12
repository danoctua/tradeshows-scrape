import datetime
from typing import List, Optional

from scrapy.http import Response
from scrapy.selector import Selector

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class HomeTextilesTodaySpider(BaseSpider):
    name = "HomeTextilesTodaySpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 21)
    EXHIBITION_NAME = "NY Textiles Market - Spring"
    EXHIBITION_WEBSITE = "https://www.hometextilestoday.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.homefashionproducts.com/i4a/memberDirectory/index.cfm?controller=memberDirectory&action=resultsListing&viewAll=1&directory_id=4&pageID=3297",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath(
            '//li[contains(@class, "searchResultsListGroupItem")]'
        )
        for exhibitor in exhibitors:
            yield self.parse_exhibitor(exhibitor, response)

    def parse_exhibitor(self, exhibitor: Selector, response: Response):
        item = self.item_loader(item=self.item(), response=response)
        exhibitor_data: List[str] = exhibitor.xpath("./p[1]//text()").getall()
        description = exhibitor.xpath("./p[2]//text()").get()
        exhibitor_name, _, _, email, address1, address2, *args = exhibitor_data
        item.add_value("exhibitor_name", exhibitor_name)
        item.add_value("email", email)
        item.add_value("address", [address1, address2])
        item.add_value("description", description)
        for key, field_name in (("Tel:", "phone"), ("Fax:", "fax")):
            index = self.get_item_index(args, key)
            if index:
                value: str = args[index]
                if value.endswith("com") or value.endswith("com/"):
                    item.add_value("website", value)
                else:
                    item.add_value(field_name, value)

        value = args[-1].strip()
        if value.endswith("com") or value.endswith("com/"):
            item.add_value("website", value)

        return item.load_item()

    def parse_exhibitors(self, response: Response):
        # replace with method parse exhibitors data
        pass

    @staticmethod
    def get_item_index(values: List[str], key: str) -> Optional[int]:
        values = [value.strip() for value in values]
        try:
            key_index = values.index(key)
            for i, item in enumerate(values[key_index + 1 :], start=1):
                if item.strip():
                    return key_index + i
        except ValueError:
            pass
        return None
