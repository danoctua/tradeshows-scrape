import datetime
import pathlib
from typing import IO

from scrapy import Item
from scrapy.exporters import CsvItemExporter

RESULTS_FOLDER = "results"
RESULTS_FILENAME_FORMAT = "Crawl-{start_datetime}.csv"


class ExportItemPipeline:

    exporter: CsvItemExporter
    file: IO

    def open_spider(self, spider):
        file_path = pathlib.Path(
            RESULTS_FOLDER,
            spider.name,
            RESULTS_FILENAME_FORMAT.format(start_datetime=datetime.datetime.now())
        )
        file_path.parent.mkdir(exist_ok=True, parents=True)
        self.file = open(file_path, "wb")
        self.exporter = CsvItemExporter(self.file, fields_to_export=spider.ONLY_FIELDS)

    def process_item(self, item: Item, spider) -> Item:
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
