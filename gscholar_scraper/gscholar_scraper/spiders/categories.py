# -*- coding: utf-8 -*-
from urlparse import urlparse, parse_qs, urljoin

from scrapy.http import Request
from scrapy.loader import ItemLoader

from gscholar_scraper.items import CategoryItem, SubCategoryItem
from gscholar_scraper.spiders.base import DBConnectedSpider


class CategoriesSpider(DBConnectedSpider):
    # Configure the spider
    name = "categories"
    allowed_domains = ["scholar.google.com"]


    pat = 'https://scholar.google.com/citations?view_op=top_venues&hl=de&vq={0}'
    # The main categories on Google Scholar
    cat_codes = ('bus','bio','chm', 'hum', 'med', 'eng', 'phy', 'soc')
    start_urls = [pat.format(cat) for cat in cat_codes]

    def parse(self, response):
        """ This function parses the categories and its subcategories on a gscholar web page.

        @url https://scholar.google.com/citations?view_op=top_venues&hl=de&vq=bus
        @returns items 1 1
        @returns requests 0 0
        @scrapes name subs
        """

        # We need the div that is 'selected' i.e. contains gs_sel as a css class
        title_xp = '//*[@id="gs_m_broad"]/div[contains(@class,\'gs_sel\')]/a/span/text()'

        item = ItemLoader(item=CategoryItem(), response=response)
        title = response.xpath(title_xp).extract_first()

        item.add_value('name', title)
        subs = []
        for sub in response.xpath('//*[@id="gs_m_rbs"]/ul/li/a'):
            s = {'name' : sub.xpath('text()').extract_first()}
            rel_url = sub.xpath('@href').extract_first()
            s['vq'] = parse_qs(urlparse(rel_url).query)[u'vq'][0]
            subs.append(s)
            req = Request(urljoin(response.url,rel_url), callback=self.parse_item)
            req.meta['parent'] = title
            yield req
        item.add_value('subs', subs)
        yield item.load_item()


    def parse_item(self, response):
        self.logger.debug('Scraping Sub-Category')
        sub_cat = SubCategoryItem()
        sub_cat['name'] = response.xpath('//*[@id="gs_m_c"]/div/h3/text()').extract_first()\
            .replace('Top-Publikationen - ', '')
        publications = dict()
        for pub in response.xpath('//*[@id="gs_cit_list_table"]/tr'):
            self.logger.debug("Publication...")
            pos = pub.xpath('td[@class="gs_pos"]/text()').extract_first()
            # skip header line
            if pos is None:
                continue
            name = pub.xpath('td[@class="gs_title"]/text()').extract_first()
            self.logger.debug("Found item %s at pos %s" % (name, pos))
            publications[name] = int(pos.replace('.', ''))

            # TODO h-index url: follow or save to item
        sub_cat['publications'] = publications
        sub_cat['parent'] = response.meta.get('parent', None)
        return sub_cat
