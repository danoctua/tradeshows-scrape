from itemloaders.processors import Join, MapCompose

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


class MobitexItemLoader(BaseItemLoader):

    booth_number_in = MapCompose(str)
    booth_number_out = Join(", ")
    hall_location_in = MapCompose(str)
    hall_location_out = Join(", ")

    @staticmethod
    def phone_in(phone_lines):
        return " ".join(phone_line.strip() for phone_line in phone_lines)
