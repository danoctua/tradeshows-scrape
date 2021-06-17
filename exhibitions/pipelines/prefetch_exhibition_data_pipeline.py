import datetime

from itemadapter import ItemAdapter
from scrapy import Item


class PrefetchExhibitionDataPipeline:

    def process_item(self, item: Item, spider) -> Item:
        adapter = ItemAdapter(item)
        adapter["exhibition_name"] = spider.EXHIBITION_NAME
        if isinstance(spider.EXHIBITION_DATE, datetime.date):
            adapter["exhibition_date"] = spider.EXHIBITION_DATE.strftime("%m/%d/%Y")
        adapter["exhibition_website"] = spider.EXHIBITION_WEBSITE
        return item
