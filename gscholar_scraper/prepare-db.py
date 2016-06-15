#! /usr/bin/env python

# Prepares the database for scrapy and the web application

import gscholar_scraper.database as db

if __name__ == '__main__':
    print 'Preparing database for use.'
    db.create_relations()
