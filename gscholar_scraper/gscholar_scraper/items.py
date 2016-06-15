# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import urllib2

import scrapy
from scrapy.item import Item, Field
from scrapy.loader.processors import TakeFirst, MapCompose
from sqlalchemy import Column, TIMESTAMP, Index, Float
from sqlalchemy import Integer, String, Boolean, Text
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class TimestampedBase(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


DeclarativeBase = declarative_base(cls=TimestampedBase)

class Website(Item):

    class Model(DeclarativeBase):
        __tablename__ = 'websites'
        name = Column(String, primary_key=True, index=True, unique=True)
        description = Column(Text)
        url = Column(String)

    name = Field()
    description = Field()
    url = Field()

class GScholarItem(Item):
    pass


def fix_string(input):
    """ Fixes URL-encoded UTF-8 strings which are then again as UTF-8 in the html source
    :param input: input strings to clean
    :return: clean input strings in unicode
    """
    return map(lambda s : urllib2.unquote(s.encode('ASCII')).decode('utf-8'), input)


class FOSItem(GScholarItem):
    """One field-of-study item."""

    class Model(DeclarativeBase):
        __tablename__ = 'labels'
        field_name = Column(String, primary_key=True, index=True, unique=True)

    field_name = scrapy.Field(input_processor=fix_string, output_processor=TakeFirst())


class CoAuthorItem(GScholarItem):

    class Model(DeclarativeBase):
        __tablename__ = 'coauthor'
        author1 = Column(String, primary_key=True)
        author2 = Column(String, primary_key=True)
        __table_args__ = (Index('co_author_idx', author1, author2),)

    author1 = scrapy.Field(output_processor=TakeFirst())
    author2 = scrapy.Field(output_processor=TakeFirst())


class AuthorItem(GScholarItem):

    class Model(DeclarativeBase):
        """Sqlalchemy authors model"""
        __tablename__ = "authors"

        id = Column(String, primary_key=True, index=True, unique=True)
        name = Column(String)

        fos = Column('fields_of_study', postgresql.ARRAY(String), nullable=True)
        cited = Column(Integer, nullable=True)
        measures = Column(postgresql.ARRAY(Integer), nullable=True)
        org = Column(String, nullable=True)
        hasCo = Column(Boolean, nullable=True)

    # general author info, when searched with label:biology e.g.
    id = scrapy.Field(output_processor=TakeFirst())
    fos = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    cited = scrapy.Field(output_processor=TakeFirst(),
                         input_processor=MapCompose(lambda input: re.match('.*([0-9]+)', input).group(1) if input else None))

    # more detailed author info, scraped from author profiles
    measures = scrapy.Field(input_processor=MapCompose(lambda s: int(s)))
    org = scrapy.Field(output_processor=TakeFirst())
    hasCo = scrapy.Field(output_processor=TakeFirst())


class DocItem(GScholarItem):

    class Model(DeclarativeBase):
        __tablename__ = "documents"
        author_id = Column(String, primary_key=True)
        title = Column(String)
        id = Column(String, primary_key=True)
        cite_count = Column(Integer, nullable=True)
        year = Column(Integer)
        # btree seems to be the default index type
        __table_args__ = (Index('doc_author_idx', author_id, id),)

    author_id = scrapy.Field(
        output_processor = TakeFirst()
    )
    title = scrapy.Field(
        output_processor = TakeFirst()
    )
    id = scrapy.Field(
        input_processor = MapCompose(lambda i: i.split(':')[-1]),
        output_processor = TakeFirst()
    )
    cite_count = scrapy.Field(
        input_processor = MapCompose(lambda i : i.strip()),
        output_processor = TakeFirst())
    year = scrapy.Field(
        output_processor = TakeFirst()
    )

class OrgItem(GScholarItem):
    pass

class CategoryItem(GScholarItem):

    # Name of the category
    name = scrapy.Field()
    # Sub-categories (we will use a dict here)
    subs = scrapy.Field()

class SubCategoryItem(GScholarItem):

    # Name of the sub-category
    name = scrapy.Field()
    # parent category name
    parent = scrapy.Field()
    # vq code in request parameter
    code = scrapy.Field()
    # top 20 list of publications listed on google scholar
    # will be a list for now
    publications = scrapy.Field()

class OrgItem(GScholarItem):

    class Model(DeclarativeBase):
        """Sqlalchemy authors model"""
        __tablename__ = "org2"

        id = Column(String, primary_key=True)
        name = Column(String)
        addr = Column(String)
        lng = Column(Float(Precision=64))
        lat = Column(Float(Precision=64))

    id = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    addr = scrapy.Field(output_processor=TakeFirst())
    lng = scrapy.Field(output_processor=TakeFirst())
    lat = scrapy.Field(output_processor=TakeFirst())
