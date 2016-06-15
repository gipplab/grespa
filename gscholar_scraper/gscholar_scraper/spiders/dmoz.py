# -*- coding: utf-8 -*-

from scrapy.selector import Selector
from scrapy.spiders import Spider
from gscholar_scraper.items import Website


class DmozSpider(Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/",
    ]

    def __init__(self, my_param=None, *args,**kwargs):
        self.logger.info('Got parameter my_param: %s ' % my_param)

    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html
        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """
        sel = Selector(response)
        sites = sel.xpath('//ul[@class="directory-url"]/li')
        items = []

        for site in sites:
            item = Website()
            item['name'] = site.xpath('a/text()').extract_first()
            item['url'] = site.xpath('a/@href').extract_first()
            try:
                item['description'] = site.xpath('text()').re('-\s[^\n]*\\r')[0]
            except IndexError:
                item['description'] = None
            items.append(item)

        return items
