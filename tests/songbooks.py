import os
import json
import unittest

from pymongo import MongoClient


class SongbookTest(unittest.TestCase):

    def setUp(self):
        # enable testing environment
        os.environ['ZPEVNIK_UNITTEST'] = 'mongodb://localhost:27017/unittest'

        # get application for testing
        from server.app import app
        self.app = app.test_client()

        # login into the application via test login endpoint
        self.app.get('/test_login')

    def tearDown(self):
        # disable testing environment
        del os.environ['ZPEVNIK_UNITTEST']

        # delete all test database entries
        mongoClient = MongoClient('mongodb://localhost:27017/unittest')
        mongoClient.drop_database('unittest')

    # TODO
    def test_something(self):
        pass
