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

    def test_song_operations(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title='ELO songbook')
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['link'].split('/')[1]

        # insert test songs for further testing
        rv = utils._post_song(self.app, title='Don\'t Bring Me Down')
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_id = song['link'].split('/')[1]

        # test wrong songbook insert
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format('000000000000000000000000'),
            content_type='application/json',
            data=json.dumps(dict()))
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # test wrong song insert
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(set=[{
                'id': '000000000000000000000000'
            }])))
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # insert song into the songbook
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(set=[{
                'id': song_id
            }])))
        assert rv.status_code == 200

        # test correct insertion
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert song_id in songbook['songs'][0]['id']
        assert len(songbook['songs']) == 1

        # edit song in the songbook
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(set=[{
                'id': song_id,
                'order': 3
            }])))
        assert rv.status_code == 200

        # check correct changes
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert song_id in songbook['songs'][0]['id']
        assert 'order' in songbook['songs'][0]
        assert songbook['songs'][0]['order'] == 3

        # delete wrong song from songbook
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(delete=['000000000000000000000000'])))
        assert rv.status_code == 200

        # check correct number of songs in the songbook
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert len(songbook['songs']) == 1

        # delete song from songbook
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(delete=[song_id])))
        assert rv.status_code == 200

        # check correct number of songs in the songbook
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert len(songbook['songs']) == 0

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_bulk_song_operations(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title='ELO songbook')
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['link'].split('/')[1]

        song_ids = []
        # insert test songs for further testing
        rv = utils._post_song(self.app, title='Don\'t Bring Me Down')
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_ids.append(song['link'].split('/')[1])

        rv = utils._post_song(self.app, title='Livin\' Thing')
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_ids.append(song['link'].split('/')[1])

        rv = utils._post_song(self.app, title='Hold On Tight')
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_ids.append(song['link'].split('/')[1])

        # insert multiple songs into the songbook
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(set=[{
                'id': song_ids[0]
            }, {
                'id': song_ids[1]
            }])))
        assert rv.status_code == 200

        # test correct insertion
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert len(songbook['songs']) == 2

        in_ids = [x['id'] for x in songbook['songs']]
        assert song_ids[0] in in_ids
        assert song_ids[1] in in_ids

        # delete and insert songs in one request
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(set=[{
                'id': song_ids[2]
            }], delete=[song_ids[0]])))
        assert rv.status_code == 200

        # test correct insertion and deletion
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert len(songbook['songs']) == 2

        in_ids = [x['id'] for x in songbook['songs']]
        assert song_ids[1] in in_ids
        assert song_ids[2] in in_ids

        # delete everything
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(dict(delete=[song_ids[0], song_ids[1], song_ids[2]])))
        assert rv.status_code == 200

        # test correct insertion and deletion
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)
        assert rv.status_code == 200
        assert len(songbook['songs']) == 0

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_active_songbook(self):
        # create songbooks for testing purposes
        # test user owned songbook
        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 0,
            'owner_unit': 0,
            'options': {},
            'songs': {},
            'cached_file': None,
            'cache_expiration': None
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 200

        # test unit owned songbook
        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 0,
            'options': {},
            'songs': {},
            'cached_file': None,
            'cache_expiration': None
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 403

        # test other songbooks
        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'options': {},
            'songs': {},
            'cached_file': None,
            'cache_expiration': None
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 403
