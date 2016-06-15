import re
import urllib2

from scrapy.http import Request
from scrapy.loader import ItemLoader

import gscholar_scraper.utils as utils
from gscholar_scraper.items import OrgItem
from gscholar_scraper.spiders.base import DBConnectedSpider


class OrgDetail(DBConnectedSpider):
    name = "org_detail"
    handle_httpstatus_list = [200, 302, 400, 402, 503]
    pattern = 'https://www.google.de/maps/place/{0}'

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # fields from the database
        self.fields = self.all_fields()


        # select a field to start at
        if self.fields:
            start_org = utils.pop_random(self.fields)
            print 'starting with org %s ' % start_org.name
            enc = urllib2.quote(start_org.name.encode('utf-8')).encode('ASCII')
            self.curr = start_org.id
            self.start_urls = [self.pattern.format(enc)]


    def all_fields(self):
        session = self.create_session()

        try:
            return session.query(OrgItem.Model).filter(OrgItem.Model.lat == None).distinct().all()
        finally:
            session.close()

    def next_label_from_db(self):
        next_label = utils.pop_random(self.fields)
        if not next_label:
            return None
        enc = urllib2.quote(next_label.name.encode('utf-8')).encode('ASCII')
        self.logger.debug('Choosing existing org %s.' % enc)
        self.curr= next_label.id
        return self.pattern.format(enc)



    def parse(self, response):
        static =  response.xpath('/html/head/meta[@property="og:image"]/@content').extract_first()
        print static
        center = re.search('center=(.*?)&',static)
        coord = center.group(1).split('%2C')

        descr = response.xpath('/html/head/meta[@property="og:description"]/@content')
        if coord and descr:
                item = ItemLoader(item=OrgItem(), response=response)
                item.add_value('id', self.curr)
                item.add_xpath('addr', '/html/head/meta[@property="og:description"]/@content')
                item.add_value('lng', coord[0])
                item.add_value('lat', coord[1])

        yield item.load_item()
        next_url = self.next_label_from_db()

        if next_url:
            yield Request(url=next_url,dont_filter=True)


