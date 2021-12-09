from typing import List, Optional

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
    join_loaded,
)


class FormLandItemLoader(BaseItemLoader):
    @staticmethod
    def category_in(categories):
        return [
            x.strip() for category_line in categories for x in category_line.split(",")
        ]

    @staticmethod
    def brands_in(brands):
        return [x.strip() for brand_line in brands for x in brand_line.split(",")]

    @staticmethod
    def manufacturers_in(manufacturers):
        return [
            x.strip()
            for manufacturer_line in manufacturers
            for x in manufacturer_line.split(",")
        ]

    @staticmethod
    def website_in(website_strings):
        return [website_string.lstrip("//") for website_string in website_strings]
