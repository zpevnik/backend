import json
import unittest

from urllib.parse import urlsplit
from pymongo import MongoClient

from server.app import app


class UserTest(unittest.TestCase):

    def setUp(self):
        # get application for testing
        self.app = app.test_client()

        # get testing mongo client and database
        self.db_name = urlsplit(app.config['MONGODB_URI']).path[1:]
        self.mongo_client = MongoClient(app.config['MONGODB_URI'])
        self.mongo_db = self.mongo_client[self.db_name]

        # login into the application via test login endpoint
        self.app.get('/test_login')

    def tearDown(self):
        # delete all test database entries
        self.mongo_client.drop_database(self.db_name)

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
        self.mongo_db['users'].insert_one({
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
        assert rv.status_code == 404
