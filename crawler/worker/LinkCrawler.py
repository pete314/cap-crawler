#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Download and store links
"""

import robotparser
import urlparse
import threading
import time
import bz2
import atexit
import sys
from datetime import datetime
from hashlib import md5
from Downloader import Downloader
from crawler.db.MongoQueue import MongoQueue
from crawler.db.CassandraWrapper import CassandraWrapper
from bs4 import BeautifulSoup

DEFAULT_AGENT = "Mozilla/5.0 (compatible; Research-bot)"


class LinkCrawler(object):

    def __init__(self, site_domain=None, start_at=None, cache=None, queue=None, max_threads=10, timeout=60, max_depth=3, user_agent=DEFAULT_AGENT, scraper=None, crawl_job=None):
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
        self.start_at = start_at if start_at else site_domain
        self.cache = cache
        self.queue = MongoQueue() if queue is None else queue
        self.max_threads = max_threads
        self.timeout = timeout
        self.user_agent = user_agent
        self.scraper = scraper
        self.crawl_job = crawl_job if crawl_job is not None else "N/A"
        self.downloader = Downloader(user_agent=user_agent)
        self.robots = None
        self.max_depth = max_depth
        self.Cassa = CassandraWrapper()
        self._clenup = self.close
        atexit.register(self._clenup)  # If collapse or ctrl-c c* session will be closed
        atexit.register(self._clenup)  # If collapse or ctrl-c c* session will be closed

    def close(self):
        """Close cassa connection"""
        self.Cassa.close()

    def threaded_executor(self):
        threads = []
        self.queue.push(self.start_at, 0)
        if self.robots is None:
            self.robots = self.parse_robots_file(self.site_domain)

        while threads or self.queue:
            # the crawl is still active
            for thread in threads:
                if not thread.is_alive():
                    # remove the stopped threads
                    threads.remove(thread)
            while len(threads) < self.max_threads and self.queue:
                thread = threading.Thread(target=self.process_queue)
                thread.setDaemon(True)
                thread.start()
                threads.append(thread)

            time.sleep(1)

        self.close()
        return True

    def process_queue(self):
        """
        Process the current queue elements
        :return:None
        """

        while True:
            try:
                record = self.queue.pop()
                if record['depth'] >= self.max_depth + 1:
                    # First occurrence of the max_depth + 1 will break the crawling
                    flushed_print_writer("+++++++++Reached maximum depth in thread")
                    self.queue.clear()
                    return

                site = record['_id'].replace(u'\u201d', '')
                next_depth = record['depth'] + 1

            except KeyError:
                """No more elements to process"""
                return
            else:
                if self.robots.can_fetch(self.user_agent, site):
                    result = self.downloader(site)
                    if result['code'] is 200:
                        flushed_print_writer("Depth %s: Processing: %s | Status: %s"
                                            % (str(record['depth']), site, str(result['code'])))

                        self.scrap_content_links(result['html'], site, next_depth=next_depth)
                        if self.scraper is None:
                            self.Cassa.insert_into('crawl_dump', {
                                'url_hash': md5(site).hexdigest(),
                                'url': site,
                                'scrape_type': 'FULL' if self.scraper is None else self.scraper,
                                'crawler_job': self.crawl_job,
                                'content': bz2.compress(result['html']).encode('hex'),
                                'created': datetime.now()
                            })
                    else:
                        self.Cassa.insert_into('crawled_links',
                                               {
                                                   'url_hash': md5(site).hexdigest(),
                                                   'url': site,
                                                   'crawler_job': self.crawl_job,
                                                   'status': result['code'],
                                                   'message': 'Error while scraping',
                                                   'created': datetime.now()
                                               })
                else:
                    flushed_print_writer("+++++++++Page blocked by robots: %s" % site)

    def scrap_content_links(self, html=None, site=None, same_domain_only=True, next_depth=0):
        """
        Regex the links from the downloaded content
        :param html: downloaded html content
        :param site: the base url to compare to
        :param same_domain_only: (True) - does not look for external links
        :param next_depth: the depth which the site scraping would execute
        :return: none
        """
        if html is not None:
            links = []
            soup = BeautifulSoup(html, 'lxml')
            for tag in soup.findAll('a', href=True):
                if tag['href'] != '#' and not links.__contains__(tag['href']):
                    link = self.normalize_link(site, tag['href'])
                    if (same_domain_only and self.check_same_domain(site, link)):
                        # THIS WILL EXCLUDE EXTERNAL LINKS AND ONLY LOOK FOR LINKS ON SAME DOMAIN
                        self.Cassa.insert_into('crawled_links',
                                               {
                                                   'url_hash': md5(site).hexdigest(),
                                                   'url': site,
                                                   'crawler_job': self.crawl_job,
                                                   'created': datetime.now()
                                               })
                        self.queue.push(link, next_depth)
                        links.append(link) # just used to filter

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


def flushed_print_writer(msg):
    sys.stdout.write("%s\n" % msg)
    sys.stdout.flush
