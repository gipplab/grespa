import random
import re
import urlparse

import scrapy
from scrapy.exceptions import NotSupported
from scrapy.http import Request
from scrapy.loader import ItemLoader
from sqlalchemy import or_

import gscholar_scraper.utils as utils
from gscholar_scraper.items import AuthorItem, DocItem, CoAuthorItem
from gscholar_scraper.models import windowed_query
from gscholar_scraper.spiders.base import DBConnectedSpider

# TODO figure out how start_authors for post request to spider...

class AuthorDetails(DBConnectedSpider):
    """ Spider that crawls the profile page of a single author for all details. It either fetches the list of already
    crawled authors (for which details are still missing) or uses the parameter `start_authors` to start with specific
    authors.
    """
    name = "author_detail"
    # handle_httpstatus_list = [200, 302, 400, 402, 503]

    pattern = 'https://scholar.google.de/citations?hl=de&user={0}&cstart=0&pagesize=100'

    def missing_authors(self):
        session = self.create_session()

        try:
            q = session.query(AuthorItem.Model).filter(or_(AuthorItem.Model.measures == None,
                                                           AuthorItem.Model.org == None,
                                                           AuthorItem.Model.hasCo == None))
            for window in windowed_query(q, AuthorItem.Model.id, 1000):
                yield window
        finally:
            session.close()

    def __init__(self, start_authors=None, *args, **kwargs):

        super(self.__class__, self).__init__(*args, **kwargs)

        # Scrape only the given authors
        self.scrape_given = len(self.start_urls) > 0


        self.missing_authors = self.missing_authors()
        # author profiles with cstart and pagesize parameters
        self.container = []

        # if we did not seed the crawler ourselves for a single author crawl
        # select a random url to start at
        if not self.start_urls and self.missing_authors:
            start_author = self.missing_authors.next()
            print 'starting with author %s' % start_author.name
            self.start_urls = [self.pattern.format(start_author.id)]

    def next_author_from_db(self):
        next_author = next(self.missing_authors, None)
        if not next_author:
            return None
        self.logger.debug('Choosing existing author %s.' % next_author.name)
        return self.pattern.format(next_author.id)

    def choose_next(self):
        # do not choose from database if we only want to scrape the given authors
        if self.scrape_given:
            return utils.pop_random(self.container)

        if random.random() > 0.5:
            if len(self.container) == 0:
                l = self.next_author_from_db()
                return l
            else:
                u = utils.pop_random(self.container)
                self.logger.debug('Choosing existing url %s.' % u)
                return u
        else:
            next_author = self.next_author_from_db()
            if next_author:
                return next_author

            next_author = utils.pop_random(self.container)
            self.logger.debug('Choosing existing url %s.' % next_author)
            return next_author

    def parse_profile(self, response, author_id, old_start):
        self.logger.info('Parsing main profile for author %s.' % author_id)

        authorItem = AuthorItem()
        authorItem['id'] = author_id

        #crawl 'organisation id' and 'measurements' only at the first time, we look at that author profile
        if old_start == 0:
            orgMatch = re.search('org=(\d+)"', response.xpath('//div[@class="gsc_prf_il"]').extract_first())
            org = orgMatch.group(1) if orgMatch else None
            co_authors_link = response.xpath('//h3/a[@class="gsc_rsb_lc"]/@href').extract_first()

            # build detailed author item
            item = ItemLoader(item=authorItem, response=response)
            # Update fields (if author was not crawled already, this fills the 'required' fields)
            item.add_xpath('name', '//*[@id="gsc_prf_in"]/text()')
            # cited (first field of measures)
            item.add_xpath('cited', '//*[@id="gsc_rsb_st"]/tbody/tr[2]/td[2]')
            # fos
            urls = response.xpath('//*[@id="gsc_prf_i"]/div/a[@class="gsc_prf_ila"]/@href').extract()
            labels = [urlparse.parse_qs(urlparse.urlparse(url).query)['mauthors'][0].split(':')[1]
                      for url in urls]

            item.add_value('fos', labels)
            # additional items
            # measures has values for citetotal, cite2010, htotal, h2010, i10total, i2010
            item.add_xpath('measures', '//td[@class="gsc_rsb_std"]/text()')
            item.add_value('org', org)
            # check if the author has any coauthors listed
            item.add_value('hasCo', 'True' if co_authors_link else 'False')
            yield item.load_item()

            # Crawl colleagues
            if co_authors_link:
                link = urlparse.urljoin(response.url, co_authors_link)
                self.logger.debug('Requesting co-authors with link %s' % link)
                yield Request(url=link)


        # crawl the author's documents

        # docid is the part in the following
        # /citations?view_op=view_citation&;hl=de&user=F4P3ghEAAAAJ&pagesize=100&citation_for_view=F4P3ghEAAAAJ:u5HHmVD_uO8C
        # to-do: id unique? same id, when document requested from another author's profile?

        # Prepare document item with authors id for reuse
        doc_item = DocItem()
        doc_item['author_id'] = author_id

        # Publication items for the author
        num_pubs = 0
        for doc in response.xpath('//*[@class="gsc_a_tr"]'):
            num_pubs += 1
            il = ItemLoader(item=doc_item, selector=doc, response=response)
            il.add_xpath('title', './td[@class="gsc_a_t"]/a/text()')
            il.add_xpath('id', './td[@class="gsc_a_t"]/a/@href')
            il.add_xpath('cite_count', './td[@class="gsc_a_c"]/a/text()')
            il.add_xpath('year', './td[@class="gsc_a_y"]//text()')
            yield il.load_item()
        self.logger.info('Scraped %d documents for author %s after item %d.' % (num_pubs, author_id, old_start))
        # btn for next documents:
        btnEnabled = response.xpath('//button[@id="gsc_bpf_next" and not(contains(@class ,"gs_dis"))]').extract_first()
        if btnEnabled:
            # there are more documents to crawl for this author!
            # build the next url on our own, as Google solves it in its JS and does not explicitly
            # include the url in the html code

            # generate next url
            newStartTmp = old_start + 100
            newStart2 = 'cstart='+str(newStartTmp)
            newUrl = response.url.replace('cstart='+str(old_start), newStart2 )


            self.container.append(newUrl)

        # proceed with another random url to randomize access pattern to gscholar
        next_url = self.choose_next()

        if next_url:
            yield Request(url=next_url)#, dont_filter=True)

    def parse_colleagues(self, response, author_id):
        self.logger.info('Parsing colleagues for author %s.' % author_id)

        # get all authors listed
        num_authors = 0
        for div in response.xpath('//*[@class="gsc_1usr gs_scl"]'):
            num_authors += 1
            name_xp = './*[@class="gsc_1usr_name"]/text()'
            id_val = urlparse.parse_qs(urlparse.urlparse(div.xpath('//*[@id="gsc_ccl"]/div[1]/div[2]/h3/a/@href').extract_first()).query)['user']
            cited_by_xp = './*[@class="gsc_1_usr_cby"]/text()'
            fos_xp = './/a[@class="gsc_co_int"]/@href' # --> ["foo", "bar",...]

            # load general author item for colleague
            co_auth = ItemLoader(item=AuthorItem(), response=response, selector=div)
            co_auth.add_value('id', id_val)
            co_auth.add_xpath('name', name_xp)
            co_auth.add_xpath('cited', cited_by_xp)
            co_auth.add_xpath('fos', fos_xp)
            yield co_auth.load_item()

            # load co-authorship
            relation = [author_id, id_val]
            relation.sort()
            co_rel = ItemLoader(item=CoAuthorItem(), response=response)
            co_rel.add_value('author1', relation[0])
            co_rel.add_value('author2', relation[1])
            yield co_rel.load_item()

        self.logger.info('Found %d colleagues for author %s.' % (num_authors, author_id))

        next_url = self.choose_next()

        if next_url:
            yield Request(url=next_url)

    def url_params(self, url):
        return

    def parse(self, response):

        # Parse query parameters
        parse_res = urlparse.urlparse(response.url)
        if parse_res.path != '/citations':
            # we only want author details, so the path has to be right
            raise scrapy.exceptions.NotSupported

        params = urlparse.parse_qs(parse_res.query)
        author_id = params['user'][0]
        c_start_param = params.get('cstart', [None])[0]
        old_start = int(c_start_param) if c_start_param else None

        # if we are on a sub-page of the author, the view will be identified
        # one document of the list: view_citation
        # co-authors:               list_colleagues
        view_op = params.get('view_op', [None])[0]

        # detect if we are on a sub-page or on the main profile page
        if not view_op:
            # main profile
            return self.parse_profile(response, author_id, old_start)
        elif view_op == 'list_colleagues':
            return self.parse_colleagues(response, author_id)
        # the next lines can be used if we want to parse the citation pages itself, so to get to more details
        # for the publications, like publisher.
        # elif view_op == 'view_citation':
        #     parse_citation(response)

