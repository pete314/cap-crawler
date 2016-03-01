#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download and store links
"""

import robotparser
import urlparse
from Downloader import Downloader
from crawler.db.MongoQueue import MongoQueue
from BeautifulSoup import BeautifulSoup

DEFAULT_AGENT = "Research bot"

class LinkCrawler(object):

    def __init__(self, site_domain=None, cache=None, queue=None, max_threads=10, timeout=60, user_agent=DEFAULT_AGENT):
        """
        Init the link crawler with the cache to process
        :param site_domain: Domain to work with
        :param cache: The Mongo cache to compare/update to
        :param queue: The Mongo based shared queue, used to store links for processing
        :param max_threads: The number of threads in execution
        :param timeout: The timeout for the cache / db connection
        :return:
        """
        self.site_domain = site_domain
        self.cache = cache
        self.queue = MongoQueue() if queue is None else queue
        self.max_threads = max_threads
        self.timeout = timeout
        self.user_agent = user_agent
        self.threads = []
        self.downloader = Downloader(user_agent=user_agent)

    def process_list(self):
        results = []
        self.queue.push(self.site_domain)
        robots = self.parse_robots_file(self.site_domain)
        while True:
            try:
                site = self.queue.pop()
            except KeyError:
                """No more elements to process"""
                break
            else:
                if robots.can_fetch(self.user_agent, site):
                    result = self.downloader(site)
                    if result['code'] is 200:
                        print ("Status for %s is %s" % (site, result['code']))
                        site_links = self.scrap_content_links(result['html'], site)
                        results.append(site_links)
                else:
                    print("Page blocked by robots")

        return results

    def scrap_content_links(self, html=None, site=None, same_domain_only=True):
        """
        Regex the links from the downloaded content
        :param html: downloaded html content
        :param site: the base url to compare to
        :param same_domain_only: (True) - does not look for external links
        :return: links[] - list of all link on page
        """
        if html is None:
            return []
        else:
            links = []
            soup = BeautifulSoup(html)
            for tag in soup.findAll('a', href=True):
                if tag['href'] != '#' and not links.__contains__(tag['href']):
                    link = self.normalize_link(site, tag['href'])
                    if (same_domain_only and self.check_same_domain(site, link)):
                        # THIS WILL EXCLUDE EXTERNAL LINKS AND ONLY LOOK FOR LINKS ON SAME DOMAIN
                        links.append(link)
                        self.queue.push(link)
                    else:
                        links.append(link)
            return links

    def normalize_link(self, site, link):
        """
        Remove hash and add site url to relative links
        :param site: The base url of the site
        :param link: The link to work with
        :return:
        """
        link, _ = urlparse.urldefrag(link)
        return urlparse.urljoin(site, link)

    def check_same_domain(self, site_base_url, check_url):
        """
        Check if url is same domain
        :param site_base_url: base url to compare to
        :param check_url: url to validate
        :return: bool
        """
        return urlparse.urlparse(site_base_url).netloc == urlparse.urlparse(check_url).netloc

    def parse_robots_file(self, base_url):
        """
        Parse the robot file if exists
        :param base_url: The base url to parse robots.txt from
        :return: RobotFileParser
        """
        parse_rf = robotparser.RobotFileParser()
        parse_rf.set_url(urlparse.urljoin(base_url, '/robots.txt'))
        parse_rf.read()
        return parse_rf
