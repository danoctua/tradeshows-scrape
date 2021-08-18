import datetime
import pathlib
from typing import IO

from scrapy import Item

from exhibitions.exporters.named_csv_item_exporter import NamedCsvItemExported

RESULTS_FOLDER = "results"
RESULTS_FILENAME_FORMAT = "Crawl-{start_datetime}.csv"


class ExportItemPipeline:

    exporter: NamedCsvItemExported
    file: IO

    def open_spider(self, spider):
        file_path = pathlib.Path(
            RESULTS_FOLDER,
            spider.name,
            RESULTS_FILENAME_FORMAT.format(start_datetime=datetime.datetime.now()),
        )
        file_path.parent.mkdir(exist_ok=True, parents=True)
        self.file = open(file_path, "wb")
        self.exporter = NamedCsvItemExported(self.file)

    def process_item(self, item: Item, spider) -> Item:
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
