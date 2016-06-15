import re
import urllib2

from scrapy.http import Request
from scrapy.loader import ItemLoader

from gscholar_scraper.items import AuthorItem, CoAuthorItem
from gscholar_scraper.models import windowed_query
from gscholar_scraper.spiders.base import DBConnectedSpider


class AuthorCo(DBConnectedSpider):
    name = "author_co"
    handle_httpstatus_list = [200, 302, 400, 402, 503]

    pattern = 'https://scholar.google.de/citations?view_op=list_colleagues&hl=de&user={0}'

    def all_fields(self):
        session = self.create_session()
        try:
            # to do: only get unprocessed author ids
            for window in windowed_query(session.query(AuthorItem.Model).filter(AuthorItem.Model.hasCo == True), AuthorItem.Model.id, 1000):
                yield window
        finally:
            session.close()

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # fields from the database
        self.fields = self.all_fields()
        # select a field to start at
        if self.fields:
            start_author = self.fields.next().id
            print 'starting with label %s ' % start_author
            enc = urllib2.quote(start_author.encode('utf-8')).encode('ASCII')
            self.start_urls = [self.pattern.format(enc)]

    def next_author_from_db(self):
        next_author = next(self.fields, None)
        if not next_author:
            return None
        enc = urllib2.quote(next_author.id.encode('utf-8')).encode('ASCII')
        self.logger.debug('Choosing existing author %s.' % enc)
        return self.pattern.format(enc)

    def parse(self, response):
        # determine current search label
        srcAuthor = response.url.split('=')[-1]

        # get 10 author divs
        for divs in response.xpath('//*[@class="gsc_1usr_name"]')[0:9]:
            user = divs.extract()
            id = re.search('citations\?user=([^&]+)(&|)',user)
            if id:
                relation = [srcAuthor,id.group(1)]
                relation.sort()

                item = ItemLoader(item=CoAuthorItem(), response=response)
                item.add_value('author1', relation[0])
                item.add_value('author2', relation[1])
                yield item.load_item()

        next_url = self.next_author_from_db()

        if next_url:
            yield Request(url=next_url)


