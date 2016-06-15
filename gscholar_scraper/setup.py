# Automatically created by: scrapyd-deploy

from setuptools import find_packages

setup_args = {
    'name'         : 'gscholar-scraper',
    'version'      : '1.0',
    'packages'     : find_packages(),
    'entry_points' : {'scrapy': ['settings = gscholar_scraper.settings']},
    # 'install_requires' : ['scrapy', 'sqlalchemy', 'psycopg2'],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    setup_args['install_requires'] = ['scrapy>=1.0', 'sqlalchemy', 'psycopg2', 'stem', 'scrapy-fake-useragent', 'python-dotenv']

setup(**setup_args)
