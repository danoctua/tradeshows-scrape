import datetime
import logging
from pathlib import Path

from scrapy import spiderloader
from scrapy.utils import project


README_LIST_OF_SPIDERS_KEY = "<!LIST_OF_SPIDERS_HERE>"
SHOW_SPIDER_NAME_KEY = "_SPIDER_NAME_"
SHOW_DATE_KEY = "\"_SHOW_DATE_\""
SHOW_NAME_KEY = "_SHOW_NAME_"
SHOW_WEBSITE_KEY = "_SHOW_WEBSITE_"

SPIDERS_MODULE_PATH = Path("exhibitions", "spiders")
TEMPLATE_SPIDER_FILE_NAME = "_template.py"

logger = logging.getLogger()


def get_all_spiders() -> list:
    """Returns list of spider names in the project"""
    settings = project.get_project_settings()
    spider_loader = spiderloader.SpiderLoader.from_settings(settings)
    spiders = spider_loader.list()
    return spiders


def prepare_readme():
    """Method to prepare the README

    If generates list of spiders and add it to the README
    """
    with open("README.md.template", "r") as source:
        data = source.read()

    spiders = get_all_spiders()
    spiders_formatted = "\n".join(f"- {spider}" for spider in spiders)
    data = data.replace(README_LIST_OF_SPIDERS_KEY, spiders_formatted)

    with open("README.md", "w") as output:
        output.write(data)

    logger.info(f"The README was prepared. {len(spiders)} were added to the template.")


def create_new_spider(show_name: str, spider_name: str, show_date: datetime.date, show_website: str):
    new_spider_file = f'{spider_name.replace(" ", "").lower()}_spider.py'
    new_spider_class_name = f'{spider_name.replace(" ", "")}Spider'
    with open(SPIDERS_MODULE_PATH / TEMPLATE_SPIDER_FILE_NAME, "r") as source:
        data = source.read()

    data = data.replace(SHOW_SPIDER_NAME_KEY, new_spider_class_name)
    data = data.replace(SHOW_DATE_KEY, f"datetime.date({show_date.year}, {show_date.month}, {show_date.day})")
    data = data.replace(SHOW_NAME_KEY, show_name)
    data = data.replace(SHOW_WEBSITE_KEY, show_website)

    with open(SPIDERS_MODULE_PATH / new_spider_file, "w") as target:
        target.write(data)
