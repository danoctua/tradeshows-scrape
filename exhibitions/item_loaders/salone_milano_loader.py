from itemloaders.processors import MapCompose

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
    join_loaded,
)


class SaloneMilanoItemLoader(BaseItemLoader):

    exhibitor_name_in = MapCompose(str.strip)

    @staticmethod
    def description_in(description):
        return join_loaded(description, separator=" ")
