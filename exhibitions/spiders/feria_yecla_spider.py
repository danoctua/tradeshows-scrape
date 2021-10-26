import datetime

from scrapy.http import Response

from exhibitions.item_loaders.feria_yecia_loader import FeriaYeciaLoader
from exhibitions.items.exhibitor import ExhibitorItem
from exhibitions.spiders.base_spiders.base_spider import BaseSpider


class FeriaYeclaSpider(BaseSpider):
    name = "FeriaYeclaSpider"

    EXHIBITION_DATE = datetime.date(2021, 10, 22)
    EXHIBITION_NAME = "Feria del mueble Yecla"
    EXHIBITION_WEBSITE = "https://en.feriayecla.com/"

    HEADERS = {}  # replace with headers dict

    item_loader = FeriaYeciaLoader
    item = ExhibitorItem

    URLS = [
        "https://en.feriayecla.com/exhibitors/",
    ]

    custom_settings = {
        "ITEM_PIPELINES": {
            "exhibitions.pipelines.prefetch_exhibition_data_pipeline.PrefetchExhibitionDataPipeline": 10,
            "exhibitions.pipelines.export_item_pipeline.ExportItemPipeline": 100,
        }
    }

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath('//h5/a[@itemprop="url"]/@href')
        yield from response.follow_all(
            exhibitors,
            callback=self.parse_exhibitors,
            headers=self.HEADERS
        )

    def parse_exhibitors(self, response: Response):
        exhibitor_item = self.item_loader(item=self.item(), response=response)
        exhibitor_name = response.xpath(
            '//div[@class="title_holder"]//h1/span/text()'
        ).re_first(r"(?P<exhibitor_name>.*)\s–\sStand\s.*")
        exhibitor_item.add_value("exhibitor_name", exhibitor_name)
        exhibitor_item.add_xpath(
            "booth_number",
            '//img[contains(@src, "stand")]/parent::div/following-sibling::div//p/text()'
        )
        exhibitor_item.add_xpath(
            "booth_number",
            '//img[contains(@src, "stand")]/parent::noscript/parent::div/following-sibling::div//p/text()'
        )
        exhibitor_item.add_xpath(
            "category",
            '//img[contains(@src, "icono-expositores.png")]/parent::noscript/parent::div/following-sibling::div//p/text()'
        )
        exhibitor_item.add_xpath(
            "email",
            '//img[contains(@src, "contacto")]/parent::noscript/parent::div/following-sibling::div//p/text()'
        )
        exhibitor_item.add_value("description", exhibitor_name)
        exhibitor_item.add_xpath(
            "description",
            '//div[contains(@class, "wpb_content_element")]//p[//*[not(name()="noscript")]]/text()'
        )
        yield exhibitor_item.load_item()
