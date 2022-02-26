import datetime

from scrapy import Selector
from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class HomeDesignSpider(BaseSpider):
    name = "HomeDesignSpider"

    EXHIBITION_DATE = datetime.date(2022, 4, 6)
    EXHIBITION_NAME = "Home Design"
    EXHIBITION_WEBSITE = "https://otthon-design.hu/en/catalogue/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://eregistrator.hu/6/index.php?ajax=kialllist1-grid&lngid=en&mode=L&orgid=00158376&page=1&pagesize=300&pridlist=CSA22%2COTD22%2CCAU22&r=kialllista%2Fkialllista1%2Flist&up=1&upevent=otthondesign",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath("//table[contains(@class, 'items')]//tr")
        for exhibitor in exhibitors[1:]:
            yield self.parse_exhibitor(response, exhibitor)

    def parse_exhibitor(self, response: TextResponse, exhibitor_selector: Selector):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        # import pdb; pdb.set_trace()
        exhibitor_name, location = exhibitor_selector.xpath("./td/text()").getall()
        hall_location, booth_number = None, None
        if location and len(location.rsplit(maxsplit=1)) == 2:
            hall_location, booth_number = location.rsplit(maxsplit=1)
        else:
            booth_number = location
        exhibitor_item.add_value("exhibitor_name", exhibitor_name)
        exhibitor_item.add_value("booth_number", booth_number)
        exhibitor_item.add_value("hall_location", hall_location)
        return exhibitor_item.load_item()
