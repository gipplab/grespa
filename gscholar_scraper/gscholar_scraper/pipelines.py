# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
import database as db
import logging

logger = logging.getLogger('scrapy')

class PostgresStoragePipeline(object):
    """A pipeline for storage of items to the database.
    """
    def __init__(self, database_settings):
        self.db_settings = database_settings

    @classmethod
    def from_crawler(cls, crawler):
        settings = db.db_settings(crawler.settings)
        logger.error('Using database \'%s\' on host \'%s\'' % (settings.get('database'),
                                                                     settings.get('host')))
        return cls(
                settings
            )

    def open_spider(self, spider):
        self.engine = create_engine(URL(**self.db_settings))
        # DeclarativeBase.metadata.create_all(self.engine)

        self.sessionmaker = sessionmaker(bind=self.engine)
        spider.logger.error('Using database \'%s\' on host \'%s\'' % (self.db_settings.get('database'),
                                                                     self.db_settings.get('host')))
        # spider.logger.info('Created sessionmaker for database %s' % self.db_settings.get('database'))

    def close_spider(self, spider):
        self.engine.dispose()

    def process_item(self, item, spider):

        session = self.sessionmaker()
        db_item = None
        if hasattr(item, 'Model'):
            db_item = item.Model(**item)

        try:
            session.merge(db_item)
            spider.logger.info('Storing model item %s' % db_item)
            session.commit()
        except Exception as e:
            spider.logger.error(e)
            session.rollback()
            raise e
        finally:
            session.close()
        return item

# we set the default values in this pipeline step
class DefaultValuesForItem(object):
    def process_item(self, item, spider):
        # if isinstance(item, items.GScholarItem):
        #     item.setdefault('updated_at', ctime())
        return item
