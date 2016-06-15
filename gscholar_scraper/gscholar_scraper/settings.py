# -*- coding: utf-8 -*-

# Scrapy settings for gscholar_scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'gscholar_scraper'

SPIDER_MODULES = ['gscholar_scraper.spiders']
NEWSPIDER_MODULE = 'gscholar_scraper.spiders'

SEED_NAME_LIST = 'names.txt'

LOG_LEVEL = 'DEBUG'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'gscholar_scraper (+http://www.isg.uni-konstanz.de/teaching/webir/)'

CONCURRENT_REQUESTS = 1
#DOWNLOAD_DELAY = 4
#RANDOMIZE_DOWNLOAD_DELAY = True

# We do not want redirects to the captcha site followed
REDIRECT_ENABLED = False

# RETRY_HTTP_CODES = [302, 400, 403]

# Our http proxy. You can use Polipo or privoxy.
# Use the urlparse.urlparse method to access the netloc (get rid of 'http').
HTTP_PROXY = 'http://127.0.0.1:8123'


# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   # 'gscholar_scraper.middlewares.RenewTorConnectionMiddleware': 0,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy.downloadermiddleware.retry.RetryMiddleware': None,

    'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
    'gscholar_scraper.middlewares.ProxyMiddleware': None,
    # TODO fix own middleware that renews tor identity
    'gscholar_scraper.middlewares.ProxiedTorConnectionMiddleware' : None,
    'gscholar_scraper.middlewares.LoggerMiddleware' : 900,
}

# DEPTH_LIMIT = 10

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED=False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'gscholar_scraper.pipelines.DefaultValuesForItem' : None,
    'gscholar_scraper.pipelines.PostgresStoragePipeline' : 900,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
#AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
