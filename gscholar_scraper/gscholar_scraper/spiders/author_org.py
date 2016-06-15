import random
import re
import urllib2

from scrapy.http import Request
from scrapy.loader import ItemLoader

import gscholar_scraper.utils as utils
from gscholar_scraper.items import AuthorItem
from gscholar_scraper.models import windowed_query
from gscholar_scraper.spiders.base import DBConnectedSpider


class AuthorOrg(DBConnectedSpider):
    name = "author_org"
    handle_httpstatus_list = [200, 302, 400, 402, 503]
    pattern = 'https://scholar.google.de/citations?view_op=view_org&hl=de&org={0}'

    def all_fields(self):
        session = self.create_session()
        try:
            for window in windowed_query(session.query(AuthorItem.Model).filter(AuthorItem.Model.org != None), AuthorItem.Model.org, 1000):
                yield window
        finally:
            session.close()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # fields from the database
        self.fields = self.all_fields()
        # appended urls from pagination
        self.container = []

        # select a field to start at
        if self.fields:
            start_org = self.fields.next().org
            print 'starting with org %s ' % start_org
            enc = urllib2.quote(start_org.encode('utf-8')).encode('ASCII')
            self.start_urls = [self.pattern.format(enc)]

    def next_label_from_db(self):
        next_label = next(self.fields, None)
        if not next_label:
            return None
        enc = urllib2.quote(next_label.org.encode('utf-8')).encode('ASCII')
        self.logger.debug('Choosing existing org %s.' % enc)
        return self.pattern.format(enc)

    def choose_next(self):
        if random.random() > 0.5:
            if len(self.container) == 0:
                l = self.next_label_from_db()
                return l
            else:
                u = utils.pop_random(self.container)
                self.logger.debug('Choosing existing url %s.' % u)
                return u
        else:
            next_url = self.next_label_from_db()
            if next_url:
                return next_url

            next_url = utils.pop_random(self.container)
            self.logger.debug('Choosing existing url %s.' % next_url)
            return next_url

    def parse(self, response):


        # get 10 author divs
        for divs in response.xpath('//div[@class="gsc_1usr gs_scl"]')[0:9]:
            user = divs.extract()

            # Content in the img's alt tag is the actual name, shown on the profile
            # However, the name in the actual link differs sometimes slightly
            # EH Roberts (link) instead of E H Roberts (on profile + alt)

            id = re.search('citations\?user=([^&]+)(&|)',user)
            name = re.search('alt="([^"]+)"', user)
            citecount = re.search('<div class="gsc_1usr_cby">Zitiert von: ([0-9]+)</div>', user)
            fostmp = re.findall('label:([^"]+)("|)', user)
            fos = [i[0] for i in fostmp]
            if id and name:
                item = ItemLoader(item=AuthorItem(), response=response)
                item.add_value('fos', fos)
                item.add_value('id', id.group(1))
                item.add_value('name', name.group(1))

                # unknown citation count:
                cited = citecount.group(1) if citecount else None
                item.add_value('cited', cited)
                yield item.load_item()

        # generate  next url
        new1 = response.xpath('//*[@id="gsc_authors_bottom_pag"]/span/button[2]').extract_first()
        if new1:
            new2 = re.search('org(.*)\'"', new1)
            if new2:
                newUrl = str(new2.group(1)).replace('\\x3d','=').replace('\\x26', '&')
                newUrl = 'https://scholar.google.de/citations?view_op=view_org&hl=de&org' + newUrl
                self.container.append(newUrl)

        # proceed with another random url or label to randomize access pattern to gscholar
        next_url = self.choose_next()

        if next_url:
            yield Request(url=next_url,dont_filter=True)


