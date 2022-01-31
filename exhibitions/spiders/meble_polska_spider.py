import datetime

from scrapy.http import TextResponse

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class MeblePolskaSpider(BaseSpider):
    name = "MeblePolskaSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 22)
    EXHIBITION_NAME = "Meble Polska"
    EXHIBITION_WEBSITE = "https://www.meblepolska.pl/en/"

    HEADERS = {}  # replace with headers dict

    item_loader = BaseItemLoader
    item = ExhibitorItem

    URLS = [
        "https://www.meblepolska.pl/en/news/last-stands-in-pavilions-available/#!#exhibitor_list",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: TextResponse):
        exhibitors = response.xpath("//div[@class='tableWrap']/table/tbody/tr")
        for exhibitor in exhibitors[1:]:  # omit the first one as it's a header
            exhibitor_item = self.item_loader(item=self.item(), response=response)
            exhibitor_name, country, website, *_ = exhibitor.xpath(
                "./td//text()"
            ).getall()
            exhibitor_item.add_value("exhibitor_name", exhibitor_name)
            exhibitor_item.add_value("country", country)
            exhibitor_item.add_value("website", website)
            yield exhibitor_item.load_item()
