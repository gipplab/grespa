from twisted.internet import reactor
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from spiders.categories import CategoriesSpider

configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

# TODO get settings to work with FEED_EXPORTERS!
proc = CrawlerProcess()

proc.crawl(CategoriesSpider())

proc.start() # block here
