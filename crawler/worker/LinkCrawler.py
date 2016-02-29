#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download and store links
"""

import Downloader

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
        while True:
            try:
                site = self.root_list.pop()
            except IndexError:
                """No more elements to process"""
                break
            else:
                downloader = Downloader(site)
                print downloader
