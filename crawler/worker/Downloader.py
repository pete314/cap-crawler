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


DEFAULT_DELAY = 10
DEFAULT_RETRY = 1
DEFAULT_TIMEOUT = 60
DEFAULT_AGENT = "xsec"


class Downloader(object):
    def __init__(self, url=None, delay_time=DEFAULT_DELAY, max_retry=DEFAULT_RETRY):
        self.url = url
        self.delay_time = delay_time
        self.max_retry = max_retry

    def __call__(self, url):
        result = None

    def download(self, url, headers, num_retries, data=None):
        """
        Simple request to download content
        :param url: The content url to donwload
        :param headers: Headers used in request
        :param num_retries:
        :param data: Post|Put data
        :return: dict('html':HTML_DATA, 'code': ERROR_CODE)
        """
        request = urllib2.Request(url, data, headers or {})
        opener = urllib2.build_opener()
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except Exception as e:
            print 'Download error:', str(e)
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if num_retries > 0 and 500 <= code < 600:
                    # retry 5XX HTTP errors
                    return self._get(url, headers, proxy, num_retries-1, data)
            else:
                code = None
        return {'html': html, 'code': code}

class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
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