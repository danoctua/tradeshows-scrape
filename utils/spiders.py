import logging

from scrapy import spiderloader
from scrapy.utils import project


README_LIST_OF_SPIDERS_KEY = "<!LIST_OF_SPIDERS_HERE>"

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
