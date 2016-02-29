#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download and store links
"""

class LinkCrawler(object):

    def __init__(self, root_list=[], cache=None):
        """
        Init the link crawler with the cache to process
        :param cache: The mongo cache to process
        :return:
        """
        self.cache = cache

