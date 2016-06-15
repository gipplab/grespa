import random, os, urllib2, time

from urlparse import urlparse
from scrapy.conf import settings
from stem import Signal, SocketClosed
from stem.control import Controller
from fake_useragent import UserAgent
from os import environ

IP_ENDPOINT = 'http://icanhazip.com/'

TOR_CONTROL_PASSWORD = 'TOR_CONTROL_PASSWORD'

ua = UserAgent()
ua.update()

class LoggerMiddleware(object):
    def process_request(self, request, spider):
        spider.logger.debug(u'User-Agent: {0} {1}'.format(request.headers['User-Agent'], request))


class ProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = settings.get('HTTP_PROXY')


def make_request(url):
    def _set_urlproxy():
        proxy_support = urllib2.ProxyHandler(
            {'http' : urlparse(settings.get("HTTP_PROXY")).netloc})
        opener = urllib2.build_opener(proxy_support)
        urllib2.install_opener(opener)
    _set_urlproxy()
    request = urllib2.Request(url, None, headers = {'User-Agent' : ua.random})
    return urllib2.urlopen(request).read().rstrip()


def renew_connection(logger, settings):
    try:
        # TODO docker file with control port and password
        with Controller.from_port(port = 9051) as controller:
            pw = environ.get(TOR_CONTROL_PASSWORD, settings.get(TOR_CONTROL_PASSWORD, default='')),
            controller.authenticate(password = pw)
            controller.signal(Signal.NEWNYM)
    except SocketClosed as e:
        logger.error(e)

class ProxiedTorConnectionMiddleware(object):
    def process_response(self, request, response, spider):
        spider.logger.debug('Got code %d.' % response.status)
        if response.status != 200 or response.headers.get('Location'):
            # we probably got redirected to the captcha page
            spider.logger.info('Response status: {0} using proxy {1} retrying request to {2}'
                               .format(response.status, request.meta['proxy'], request.url))

            # Retry a number of times, before we really need to renew the IP
            # TODO figure out how to exactly reschedule the request for a later time and not as the next one
            max_retries = 3
            retries_left = int(request.headers.get('Retry-Count', max_retries))
            if (retries_left > 0):
                # we have still retries left
                request.headers['Retry-Count'] = retries_left - 1
                request.headers['User-Agent'] = ua.random
                spider.logger.debug('Retrying ({0} left) {1}'.format(retries_left, request.url))
                return request.replace(dont_filter=True, priority=-50)

            spider.logger.error('Redirect url %s' % request.url)
            spider.logger.error('User-Agent: %s' % request.headers['User-Agent'])

            old_ip = make_request(IP_ENDPOINT)
            renew_connection(spider.logger, spider.settings)
            new_ip = make_request(IP_ENDPOINT)
            seconds = 0

            while old_ip == new_ip:
                sleep = 2
                time.sleep(sleep)
                seconds += sleep
                new_ip = make_request(IP_ENDPOINT)
                spider.logger.error('%d seconds waiting for new IP address' % seconds)
            spider.logger.error('Got new IP: %s' % new_ip)

            wait = 30
            spider.logger.debug('Waiting %s seconds for retry.' % wait)
            time.sleep(wait)
            # retry the request again with the new location
            request.headers['User-Agent'] = ua.random
            req = request.replace(dont_filter=True, priority=-50)
            spider.logger.debug('Rescheduling request %s' % req)
            return req
        return response

    def process_exception(self, request, exception, spider):
        spider.logger.error('Exception with {0} in {1}'.format(request.meta['proxy'], request.url))
