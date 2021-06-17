from scrapy import Item


class FilterFieldsPipeline:

    def process_item(self, item: Item, spider) -> Item:
        if spider.NO_SOCIAL:
            item.fields = {k: v for (k, v) in item.items() if v.get("social")}
        return item
