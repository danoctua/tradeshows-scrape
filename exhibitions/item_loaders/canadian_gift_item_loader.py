import re

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


PHONE_REGEX = re.compile(f"Phone: (?P<phone_number>.*)")
FAX_REGEX = re.compile(f"Fax: (?P<fax_number>.*)")


class CanadianGiftItemLoader(BaseItemLoader):
    @staticmethod
    def phone_in(phone_lines_in):
        return [
            x for phone_line in phone_lines_in for x in PHONE_REGEX.findall(phone_line)
        ]

    @staticmethod
    def fax_in(fax_lines_in):
        return [x for fax_line in fax_lines_in for x in FAX_REGEX.findall(fax_line)]
