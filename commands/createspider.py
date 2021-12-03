import datetime

from scrapy.commands import ScrapyCommand

from utils.spiders import create_new_spider


QUIT_COMMAND = "q"


class Command(ScrapyCommand):

    requires_project = True

    def short_desc(self):
        return "Create trade show spider from template"

    def run(self, args, opts):
        show_name: str = ""
        while not show_name:
            show_name = input(
                "Please enter the trade show name as it will be populated to the report."
                "\n\tThe show name: "
            )
            if show_name == QUIT_COMMAND:
                exit(0)
            if not show_name:
                print("Please enter a valid show name! Or enter q to quit.")

        print(f"The new show name is: {show_name}.")
        spider_name = input(
            "Please enter spider name without any special characters. "
            "\nE.g.: New Show"
            "\nIt will be converted to the NewShowSpider class in the file named new_show_spider.py."
            "\nIf you want it to be the same as the show name, please hit the ENTER button."
            "\n\tThe new spider name: "
        )
        spider_name = spider_name or show_name
        print(f"The new spider name is: {spider_name}.")
        show_date_str: str = input(
            "Please enter the show date in the MM/DD/YYYY format." "\n\tThe show date: "
        )
        show_date = datetime.datetime.strptime(show_date_str, "%d/%m/%Y").date()
        print(f"The show date is {show_date}")
        show_website: str = input(
            "Please enter the show website" "\n\tThe show website: "
        )
        create_new_spider(
            spider_name=spider_name,
            show_name=show_name,
            show_date=show_date,
            show_website=show_website,
        )
        print(f"New spider for the show {show_name} was successfully created!")
