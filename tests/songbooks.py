import json
import unittest
import tests.utils as utils

from urllib.parse import urlsplit
from bson import ObjectId
from pymongo import MongoClient

from server.app import app


class SongbookTest(unittest.TestCase):

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

    def test_songbook_basics(self):
        # check empty database get request
        rv = self.app.get('/api/v1/songbooks')
        assert rv.status_code == 200
        assert b'[]' in rv.data

        # add songbook into the database
        rv = utils._post_songbook(self.app, title='My songbook')
        assert rv.status_code == 201
        assert b'"link": "songbooks/' in rv.data

        # get songbooks with get request
        rv = self.app.get('/api/v1/songbooks')
        assert rv.status_code == 200

        # get id of one of the songs
        res = json.loads(rv.data)
        songbook_id = res['data'][0]['id']

        # check get request on selected songbook
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 200
        songbook = json.loads(rv.data)
        assert songbook['title'] == 'My songbook'
        assert songbook['id'] == songbook_id

        # test put (edit) request
        rv = utils._put_songbook(self.app, songbook_id, title='Other songbook')
        assert rv.status_code == 200
        songbook = json.loads(rv.data)
        assert songbook['title'] == 'Other songbook'
        assert songbook['id'] == songbook_id

        # test get request on edited songbook
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 200
        songbook = json.loads(rv.data)
        assert songbook['title'] == 'Other songbook'
        assert songbook['id'] == songbook_id

        # add more songbooks into the database
        rv = utils._post_songbook(self.app, title='Good songbook')

        # remember size of the database
        rv = self.app.get('/api/v1/songbooks')
        res = json.loads(rv.data)
        temp = res['count']

        # delete songbbok from the database
        rv = self.app.delete('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 204

        # check, that songbook is really deleted
        rv = self.app.get('/api/v1/songbooks')
        res = json.loads(rv.data)
        assert res['count'] == temp - 1

        # check that songbook cannot be found via its id
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 404
        assert b'Songbook was not found' in rv.data

        # try to delete nonexistent songbook from the database
        rv = self.app.delete('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 404

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_post_requests(self):
        # test json request error
        rv = self.app.post('/api/v1/songbooks')
        assert rv.status_code == 400

        # test missing fields
        rv = self.app.post(
            '/api/v1/songbooks',
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_put_request(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title='My songbook')
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['link'].split('/')[1]

        # test wrong songbook id
        rv = utils._put_songbook(self.app, '000000000000000000000000', title='Other songbook')
        assert rv.status_code == 404

        # test missing fields
        rv = self.app.put(
            '/api/v1/songbooks/{}'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)
