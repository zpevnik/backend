import os
import json
import unittest

from pymongo import MongoClient


class UserTest(unittest.TestCase):

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

    def test_user_basics(self):
        # check user info
        rv = self.app.get('/api/v1/user')
        assert rv.status_code == 200
        assert b'"active_songbook": ' in rv.data
        assert b'"logout_link": ' in rv.data
        assert b'"name": ' in rv.data

    def test_login_page(self):
        # check login page accessibility
        rv = self.app.get('/')
        assert rv.status_code == 200
