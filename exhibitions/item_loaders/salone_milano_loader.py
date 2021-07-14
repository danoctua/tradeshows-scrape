from itemloaders.processors import TakeFirst, MapCompose

from exhibitions.item_loaders.base_item_loader import BaseItemLoader


class SaloneMilanoItemLoader(BaseItemLoader):
    default_output_processor = TakeFirst()

    exhibitor_name_in = MapCompose(str.strip)

    @staticmethod
    def description_in(description):
        return " ".join([d.strip() for d in description if d and d.strip()])
