# Trade Shows scrapping tool

[![.github/workflows/python-app.yml](https://github.com/daniktl/tradeshows-scrape/actions/workflows/python-app.yml/badge.svg)](https://github.com/daniktl/tradeshows-scrape/actions/workflows/python-app.yml)


Simple scrapping tool for extracting exhibitors data from the trade shows pages.

Current features:
* base spider with generating start request[s].
* base exhibitor item with predefined fields (add new fields if required).
* export-to-csv pipeline [crawls for each spider are grouped in the folders].


## Configuration

To use this tool, be sure to install all dependencies from the `requirements.txt` file.

## Development

### Automatic

There's a custom command to create new trade show spider: `scrapy createspider`.

You'll have to enter some required fields for the spider, and the core be generated from the template without any manual actions.

### Manual

To create new spider you have to make the following steps:

* check if spider exists for this trade show.
* if not, create spider file in the `spiders` folder (let's keep the same convention here: `trade_show_name_spider.py`).
  * inherit after the `BaseSpider` (or any existing base spider) which for now provides `start_requests` method.
  * add the following variables:
    * `name` - basic spider name that you could refer for later and that would be used to identify scrapped data.
    * `EXHIBITION_DATE`, `EXHIBITION_NAME`, `EXHIBITION_WEBSITE` - from the ticket description.
    * `URLS` - initial urls where we would extract exhibitors list from.
    * [optional] `HEADERS` - headers you want to send along with the initial request.
  * override two methods:
    * `fetch_exhibitors` - callback for initial urls. Select exhibitors here and add callback to the next method.
    * `parse_exhibitors` - extract exhibitor data and `yield` the `Exhibitor` item from this method.

### Pipelines
Currently, available pipelines (please add a simple documentation when you're creating new one):
* `PrefetchExhibitionDataPipeline` - pipeline which insert exhibition data you've provided as spider attribute.
* `ExportItemPipeline` - exports item to the CSV file.

### Middlewares
Available middlewares:
* `ProxyDownloaderMiddleware` - middleware to set proxy for spider requests.
  Remember to set the `PROXY` attribute for spider if you're using this middleware.
  See middleware documentation and usages for more details.
* `ProxySessionMiddleware` - the same as above, but provides useful in some cases feature - keeping the same IP for all the requests.
  Currently, this is a proxy-dependent feature as the only Zyte is supporting this, but it maybe extended for other proxies as well.

## Running

To run your crawl, execute the following command in the root folder: `scrapy crawl [SPIDER_NAME]`

After you'd see the logs and output of the spider. Spider finish execution after it fetched all data.

Go to the `result/[SPIDER_NAME]` and you would find all crawl results here. Naming format is `Crawl-[CRAWL_START_DATETIME].csv`.

Feel free to use it and add some docs here when you create useful pipelines/middlewares.

## List of supported trade shows

_This list is generated with the `scrapy readme` command._

- _SPIDER_NAME_
- AAHQASpider
- AmbienteSpider
- AtlantaGiftSpider
- BarAndRestaurantSpider
- BDNYSpider
- CanadianGiftSpider
- CasualMarketSpider
- ChristmasWorldSpider
- CoveringsSpider
- DallasMarketSpider
- DomotexSpider
- EcommerceSpider
- EdSpacesSpider
- ExponorSpider
- FeriaYeclaSpider
- ForGardenSpider
- FormexSpider
- FormLandSpider
- FurnitureManufacturingSpider
- FurnitureManufacturersSpider
- GivingLivingSpider
- GlobalPetExpoSpider
- HarrogateFairSpider
- HDExpoSpider
- HearthPatioSpider
- HeimTextilSpider
- HighPointMarketSpider
- HomeTextilesTodaySpider
- HomeBuildingRenovationSpider
- HomiMilanoSpider
- IBSSpider
- ImmCologneSpider
- InspiredHomeShowSpider
- InstanbulFurnitureSpider
- InterGiftSpider
- InternationalRestaurantSpider
- JanuaryFurnitureSpider
- JDCSpider
- KBBSpider
- KBISSpider
- KiffSpider
- LasVegasMarketSpider
- LichtwocheSauerlandSpider
- LightBuildingSpider
- LightFairSpider
- MadeInCanadaSpider
- MadisonSpider
- MaisonObjetSpider
- MeblePolskaSpider
- MobitexSpider
- NationalHardwareShowSpider
- NeoconHubSpider
- NewYorkNowSpider
- PartnertageSpider
- PoolSpaPatioSpider
- ProsperSpider
- SaloneMilanoSpider
- ShkessenSpider
- SportsTaligateSpider
- SpringFairSpider
- StockholmFurnitureSpider
- SuperZooSpider
- SurfacesSpider
- TopDrawerSpider
- ToyFairSpider