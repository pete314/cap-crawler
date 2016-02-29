#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download and store links
"""

from Downloader import Downloader
import re
from collections import defaultdict
from BeautifulSoup import BeautifulSoup

class LinkCrawler(object):

    def __init__(self, root_list=[], cache=None, max_threads=10, timeout=60):
        """
        Init the link crawler with the cache to process
        :param cache: The mongo cache to process
        :param root_list: List of root url to process and
        :return:
        """
        self.cache = cache
        self.root_list = root_list
        self.max_threads = max_threads
        self.timeout = timeout
        self.threads = []

    def process_list(self):
        print(len(self.root_list))
        results = []
        while True:
            try:
                site = self.root_list.pop()
            except IndexError:
                """No more elements to process"""
                break
            else:
                downloader = Downloader()
                result = downloader(site)
                if result['code'] is 200:
                    print ("Status for %s is %s" % (site, result['code']))
                    site_links = self.scrap_content_links(result['html'], site)
                    results.append(site_links)

        return results

    def scrap_content_links(self, html=None, site=None):
        """
        Regex the links from the downloaded content
        :param html: downloaded html content
        :return: links[] - list of all link on page
        """
        if html is None:
            return []
        else:
            links = []
            soup = BeautifulSoup(html)
            for tag in soup.findAll('a', href=True):
                if tag['href'] != '#' and not links.__contains__(tag['href']):
                    links.append(tag['href'])
            return links
