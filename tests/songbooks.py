import json
import unittest
import tests.utils as utils

from urllib.parse import urlsplit
from bson import ObjectId
from pymongo import MongoClient

from server.app import app
from server.constants import OPTIONS


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
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

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
        songbook_id = songbook['id']

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
        assert b'"data": "songs"' in rv.data
        assert b'"data": "options"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_variants_in_songbook(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title='My songbook')
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['id']

        # insert test song into the database
        rv = utils._post_song(self.app, title='Panic Station', description='First variant')

        assert rv.status_code == 201

        variant_ids = []

        data = json.loads(rv.data)
        song_id = data['id']
        variant_ids.append(data['variants'][0]['id'])

        # insert one more variant for this song
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(text="[verse]", description="Second variant")))
        assert rv.status_code == 201

        data = json.loads(rv.data)
        variant_ids.append(data['id'])

        # get songbooks with get request
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        assert rv.status_code == 200

        songbook = json.loads(rv.data)

        # put one variant into songbook
        songbook['songs'] = [{'variant_id': variant_ids[1]}]
        rv = self.app.put(
            '/api/v1/songbooks/{}'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(songbook))

        assert rv.status_code == 200
        assert variant_ids[0].encode() not in rv.data
        assert variant_ids[1].encode() in rv.data

        # test both songs
        songbook['songs'] = [{'variant_id': variant_ids[0]}, {'variant_id': variant_ids[1]}]
        rv = self.app.put(
            '/api/v1/songbooks/{}'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(songbook))

        assert rv.status_code == 200
        assert variant_ids[0].encode() in rv.data
        assert variant_ids[1].encode() in rv.data

        # test songbook duplication
        rv = self.app.get('/api/v1/songbooks/{}/duplicate'.format(songbook_id))
        assert rv.status_code == 201
        assert songbook_id.encode() not in rv.data
        assert b'"link": "songbooks/' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_simple_requests(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title='My songbook')
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['id']

        # test songbook title endpoint (missing title)
        rv = self.app.put(
            '/api/v1/songbooks/{}/title'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # test songbook title endpoint (no title)
        rv = utils._put_songbook_title(self.app, songbook_id, title='')
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # test songbook title endpoint (correct title)
        rv = utils._put_songbook_title(self.app, songbook_id, title='Other songbook')
        assert rv.status_code == 200
        songbook = json.loads(rv.data)
        assert songbook['title'] == 'Other songbook'
        assert songbook['id'] == songbook_id

        # test songbook songs endpoint (missing songs array)
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "songs"' in rv.data

        # test songbook songs endpoint (wrong songs)
        rv = utils._put_songbook_songs(
            self.app, songbook_id, songs=[{
                'variant_id': '000000000000000000000000'
            }])
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # insert songs into the database for further testing
        variant_ids = []

        rv = utils._post_song(self.app)
        data = json.loads(rv.data)
        variant_ids.append(data['variants'][0]['id'])

        rv = utils._post_song(self.app)
        data = json.loads(rv.data)
        variant_ids.append(data['variants'][0]['id'])

        # test songbook songs endpoint (correct insertion)
        rv = utils._put_songbook_songs(
            self.app,
            songbook_id,
            songs=[{
                'variant_id': variant_ids[0]
            }, {
                'variant_id': variant_ids[1]
            }])
        assert rv.status_code == 200
        assert variant_ids[0].encode() in rv.data
        assert variant_ids[1].encode() in rv.data

        rv = utils._put_songbook_songs(
            self.app, songbook_id, songs=[{
                'variant_id': variant_ids[0]
            }])
        assert rv.status_code == 200
        assert variant_ids[0].encode() in rv.data
        assert variant_ids[1].encode() not in rv.data

        rv = utils._put_songbook_songs(
            self.app, songbook_id, songs=[{
                'variant_id': variant_ids[1]
            }])
        assert rv.status_code == 200
        assert variant_ids[0].encode() not in rv.data
        assert variant_ids[1].encode() in rv.data

        # test songbook options endpoint (missing options)
        rv = self.app.put(
            '/api/v1/songbooks/{}/options'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "options"' in rv.data

        # test songbook options endpoint (wrong format option)
        rv = utils._put_songbook_options(self.app, songbook_id, options={'format': "B4"})
        assert rv.status_code == 422
        assert b'"code": "wrong_value"' in rv.data
        assert b'"data": "format"' in rv.data

        # test songbook options endpoint (correct change)
        rv = utils._put_songbook_options(
            self.app, songbook_id, options={
                'format': OPTIONS.FORMAT.A5,
                'chorded': False
            })
        res = json.loads(rv.data)
        assert rv.status_code == 200
        assert res['options']['format'] == OPTIONS.FORMAT.A5
        assert res['options']['chorded'] == False

        # clean the database
        self.mongo_client.drop_database(self.db_name)
