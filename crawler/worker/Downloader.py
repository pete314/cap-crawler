#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download sites
"""

import urlparse
import urllib2
import random
import time
from datetime import datetime, timedelta
import socket
import sys


DEFAULT_DELAY = 20
DEFAULT_RETRY = 1
DEFAULT_TIMEOUT = 30
DEFAULT_AGENT = "Mozilla/5.0 (compatible; Research-bot)"


class Downloader(object):
    def __init__(self, url=None, delay_time=DEFAULT_DELAY, max_retry=DEFAULT_RETRY, user_agent=DEFAULT_AGENT, html_only=True):
        self.url = url
        self.delay_time = delay_time
        self.max_retry = max_retry
        self.user_agent = user_agent
        self.html_only = html_only

    def __call__(self, url):
        result = None
        if result is None:
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, num_retries=self.max_retry)

        return result

    def download(self, url, headers, num_retries, data=None):
        """
        Simple request to download content
        :param url: The content url to download
        :param headers: Headers used in request
        :param num_retries:
        :param data: Post|Put data
        :return: dict('html':HTML_DATA, 'code': ERROR_CODE)
        """
        request = urllib2.Request(url, data, headers or {})
        opener = urllib2.build_opener()
        try:
            response = opener.open(request)
            info = response.info()

            if self.html_only and "text/html" not in info['content-type']:
                return {'html': None, 'code': 994}

            html = response.read()
            code = response.code
        except Exception as e:
            print '\n+++++++++Download error: %s, url:%s\n' % (str(e), url)
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    # retry 5XX HTTP errors
                    return self._get(url, headers, num_retries-1, data)
            else:
                code = None
        return {'html': html, 'code': code}

class Throttle:
    """Sleep between downloads from same domain
    """
    def __init__(self, delay):
        self.delay = delay
        self.domains = {}

    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urlparse.urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
