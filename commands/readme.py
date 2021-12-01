from scrapy.commands import ScrapyCommand

from utils.spiders import prepare_readme


class Command(ScrapyCommand):

    requires_project = True

    def short_desc(self):
        return "Prepare README by generating list of available spiders"

    def run(self, args, opts):
        prepare_readme()
