import datetime

from itemadapter import ItemAdapter
from scrapy import Item

from exhibitions.constants import SUBMITTED_BY


class PrefetchExhibitionDataPipeline:
    def process_item(self, item: Item, spider) -> Item:
        adapter = ItemAdapter(item)
        adapter["show_name"] = spider.EXHIBITION_NAME
        if isinstance(spider.EXHIBITION_DATE, datetime.date):
            adapter["show_date"] = spider.EXHIBITION_DATE.strftime("%m/%d/%Y")
            adapter["show_year"] = spider.EXHIBITION_DATE.year
        adapter["show_website"] = spider.EXHIBITION_WEBSITE
        adapter["submitted_by"] = SUBMITTED_BY
        return item
