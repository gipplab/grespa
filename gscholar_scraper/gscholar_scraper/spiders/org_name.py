import urllib2

from scrapy.http import Request
from scrapy.loader import ItemLoader

import gscholar_scraper.utils as utils
from gscholar_scraper.items import AuthorItem, OrgItem
from gscholar_scraper.spiders.base import DBConnectedSpider


class OrgName(DBConnectedSpider):
    name = "org_name"
    handle_httpstatus_list = [200, 302, 400, 402, 503]
    pattern = 'https://scholar.google.de/citations?view_op=view_org&hl=de&org={0}'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # fields from the database
        self.fields = self.all_fields()


        # select a field to start at
        if self.fields:
            start_org = utils.pop_random(self.fields).org
            print 'starting with org %s ' % start_org
            enc = urllib2.quote(start_org.encode('utf-8')).encode('ASCII')
            self.curr = enc
            self.start_urls = [self.pattern.format(enc)]

    def all_fields(self):
        session = self.create_session()

        try:
            return (session.query(AuthorItem.Model.org).filter(AuthorItem.Model.org != None)).distinct().all()
        finally:
            session.close()

    def next_label_from_db(self):
        next_label = utils.pop_random(self.fields)
        if not next_label:
            return None
        enc = urllib2.quote(next_label.org.encode('utf-8')).encode('ASCII')
        self.logger.debug('Choosing existing org %s.' % enc)
        self.curr= enc
        return self.pattern.format(enc)



    def parse(self, response):
        item = ItemLoader(item=OrgItem(), response=response)
        item.add_value('id', self.curr)
        item.add_xpath('name', '//h2[@class="gsc_authors_header"]/text()')
        yield item.load_item()
        next_url = self.next_label_from_db()

        if next_url:
            yield Request(url=next_url,dont_filter=True)


