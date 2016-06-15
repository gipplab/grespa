from os import environ

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

from items import DeclarativeBase

DB_HOST = 'DB_HOST'
DB_PORT = 'DB_PORT'
DB_USERNAME = 'DB_USERNAME'
DB_PASSWORD = 'DB_PASSWORD'
DB_DATABASE = 'DB_DATABASE'

def create_relations(settings=None):
    s = settings if settings else db_settings()
    engine = create_engine(URL(**s))
    DeclarativeBase.metadata.create_all(engine)

def get_from_environ_or_scrapy(key, default, scrapy_settings=None):
    return environ.get(key, scrapy_settings.get(key, default=default) if scrapy_settings else default)

def db_settings(scrapy_settings=None):
    """Returns the Postgres database connection. It reads the credentials
    from environment variables or crawler settings (env vars preferred).
    """
    return {
                    'drivername' : 'postgres',
                    'host' : get_from_environ_or_scrapy(DB_HOST, 'localhost', scrapy_settings=scrapy_settings),
                    'port' : get_from_environ_or_scrapy(DB_PORT, '5432', scrapy_settings=scrapy_settings),
                    'username' : get_from_environ_or_scrapy(DB_USERNAME, 'postgres', scrapy_settings=scrapy_settings),
                    'password' : get_from_environ_or_scrapy(DB_PASSWORD, 'postgres', scrapy_settings=scrapy_settings),
                    'database' : get_from_environ_or_scrapy(DB_DATABASE, 'postgres', scrapy_settings=scrapy_settings),
    }
