#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: 29 Jan 2016
Description:  MongoDb based cache for fast changing shared data
"""
from datetime import datetime, timedelta
from pymongo import MongoClient, errors


class MongoQueue(object):
    WAITING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, timeout=300, database_name=None, host=None, port=None):
        """
        Init the current database connection to certain database
        :param database_name: the database to connect to
        :return:
        """
        self.client = MongoClient() if client is None else client
        self.db = self.client.cache
        self.timeout = timeout

    def __nonzero__(self):
        """Returns true if there are more elements in queue
        """
        record = self.db.crawl_queue.find_one(
            {'status': {'$ne': self.COMPLETE}}
        )
        return True if record else False

    def push(self, url, depth):
        """Add a url to queue if does not exist
        """
        try:
            self.db.crawl_queue.insert({'_id': url, 'status': self.WAITING, 'depth': depth})
        except errors.DuplicateKeyError as e:
            pass # already in queue

    def pop(self):
        """Get a waiting URL from the queue and set its status to processing.
        """
        record = self.db.crawl_queue.find_and_modify(
            query={'status': self.WAITING},
            update={'$set': {'status': self.PROCESSING, 'timestamp': datetime.now()}}
        )
        if record:
            return record
        else:
            self.repair()
            raise KeyError()

    def peek(self):
        """Get a waiting url from the begining of the queue"""
        record = self.db.crawl_queue.find_and_modify(
            query={'status': self.WAITING},
            update={'$set': {'status': self.PROCESSING, 'timestamp': datetime.now()}}
        )
        if record:
            return record

    def complete(self, url):
        self.db.crawl_queue.update({'_id': url}, {'$set': {'status': self.COMPLETE}})

    def repair(self):
        """Release stalled jobs
        """
        record = self.db.crawl_queue.find_and_modify(
            query={
                'timestamp': {'$lt': datetime.now() - timedelta(seconds=self.timeout)},
                'status': {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.WAITING}}
        )
        if record:
            print '+++++++++Released:', record['_id']

    def clear(self):
        self.db.crawl_queue.drop()

