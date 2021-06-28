from scrapy.exporters import CsvItemExporter


class NamedCsvItemExported(CsvItemExporter):

    def _write_headers_and_set_fields_to_export(self, item):
        if self.include_headers_line:
            if not self.fields_to_export:
                # use declared field names, or keys if the item is a dict
                self.fields_to_export = {k: item.get(k, "") for k in item.get_order()}
            with_custom_headers = {item.fields[k].get("field_name") or k: v for (k, v) in self.fields_to_export.items()}
            row = list(self._build_row(with_custom_headers))
            self.csv_writer.writerow(row)
