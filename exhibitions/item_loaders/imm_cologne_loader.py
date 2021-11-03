from itemloaders.processors import Join

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader


class ImmCologneLoader(BaseItemLoader):

    booth_number_out = Join(" | ")
    hall_location_out = Join(" | ")

    @staticmethod
    def brands_in(brands):
        return [brand.strip() for brand in brands if brand.strip()]
