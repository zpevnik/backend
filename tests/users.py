import os
import json
import unittest

from pymongo import MongoClient


class UserTest(unittest.TestCase):

    def setUp(self):
        # enable testing environment
        os.environ['ZPEVNIK_UNITTEST'] = 'mongodb://localhost:27017/unittest'
        self.mongo_client = MongoClient('mongodb://localhost:27017/unittest')

        # get application for testing
        from server.app import app
        self.app = app.test_client()

        # login into the application via test login endpoint
        self.app.get('/test_login')

    def tearDown(self):
        # disable testing environment
        del os.environ['ZPEVNIK_UNITTEST']

        # delete all test database entries
        self.mongo_client.drop_database('unittest')

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

    def test_user_basics(self):
        # insert some test users into the database
        self.mongo_client['unittest']['users'].insert_one({
            '_id': 1001,
            'name': 'John Bonham',
            'token': 0,
            'created': 0,
            'last_login': 0,
            'active_songbook': None,
            'active': True,
            'unit': 1001,
        })

        # check test user get request
        rv = self.app.get('/api/v1/users/{}'.format(0))
        assert rv.status_code == 200
        assert b'Test' in rv.data

        # check inserted user get request
        rv = self.app.get('/api/v1/users/{}'.format(1001))
        assert rv.status_code == 200
        assert b'John Bonham' in rv.data

        # check nonexisting user
        rv = self.app.get('/api/v1/users/{}'.format(1002))
        assert rv.status_code == 422
