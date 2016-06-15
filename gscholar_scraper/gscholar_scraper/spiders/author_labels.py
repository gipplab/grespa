import scrapy
import re
from gscholar_scraper.items import FOSItem
from scrapy.http import Request
from scrapy.loader import ItemLoader
import gscholar_scraper.utils as utils
from scrapy.utils.project import get_project_settings

import urllib

from gscholar_scraper.spiders.base import DBConnectedSpider

class AuthorLabels(DBConnectedSpider):
    name = "author_labels"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    base_url = 'https://scholar.google.de/citations?view_op=search_authors&mauthors'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        settings = get_project_settings()
        with open(settings['SEED_NAME_LIST'], mode='r') as f:
            self.container = [(self.base_url + '={0}').format(urllib.quote(i)) for i in f.readlines() if len(i) > 0]

        self.logger.info('Starting with %d surnames.', len(self.container))

        start = utils.pop_random(self.container)
        if start:
            self.start_urls = [start]


    def parse(self, response):
        # for each author ID on the page,create a new authorItem
        for ids in response.xpath('//*[@id="gsc_ccl"]/div/div/div[@class="gsc_1usr_int"]'):
            full = ids.extract()
            fos = re.findall('=label:([^"]+)"', full)
            if fos:
                for f in fos:
                    it = ItemLoader(item=FOSItem(), response=response)
                    self.logger.debug(f)
                    it.add_value('field_name', f)
                    yield it.load_item()

        # generate  next url
        new1 = response.xpath('//*[@id="gsc_authors_bottom_pag"]/span/button[2]').extract_first()
        if new1:
            new2 = re.search('mauthors(.*)\'"', new1)
            if new2:
                newUrl = str(new2.group(1)).replace('\\x3d','=').replace('\\x26', '&')
                newUrl = self.base_url + newUrl
                self.container.append(newUrl)
        # proceed with another random url to randomize access pattern to gscholar
        next = utils.pop_random(self.container)
        if next:
            yield Request(url=next)


