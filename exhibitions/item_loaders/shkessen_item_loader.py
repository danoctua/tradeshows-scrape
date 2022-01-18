import re
from typing import List, Optional

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
    join_loaded,
)

EMAIL_REGEX = re.compile(r"mailto:(?P<email>.*)")


class ShkessenItemLoader(BaseItemLoader):
    pass

    @staticmethod
    def email_in(emails: List) -> list:
        return [e for email in emails for e in EMAIL_REGEX.findall(email)]
