import json
import unittest
import tests.utils as utils

from urllib.parse import urlsplit
from pymongo import MongoClient

from server.app import app
from server.constants import PERMISSION


class SongVariantTest(unittest.TestCase):

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

    def test_song_variant_basics(self):
        # add test song into the database
        rv = utils._post_song(self.app, title='Back in Black', description='Variant test song')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']
        variant_id = data['variants'][0]['id']

        # get song variant with get request
        rv = self.app.get('/api/v1/songs/{}/variants'.format(song_id))
        assert rv.status_code == 200

        # get id of song variant
        res = json.loads(rv.data)
        assert variant_id == res[0]['id']

        # check get request on selected song variant
        rv = self.app.get('/api/v1/songs/{}/variants/{}'.format(song_id, variant_id))
        assert rv.status_code == 200
        variant = json.loads(rv.data)
        assert variant['id'] == variant_id
        assert variant['description'] == "Variant test song"

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_post_requests(self):
        # insert test song into the database
        rv = utils._post_song(self.app, title='Back in Black', description='Variant test song')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']
        variant_id = data['variants'][0]['id']

        # test json request error
        rv = self.app.post('/api/v1/songs/{}/variants'.format(song_id))
        assert rv.status_code == 400

        # test missing fields
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data

        # test missing text field
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(description="Missing text variant")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "text"' in rv.data

        # test missing description field
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(text="Missing description variant")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "description"' in rv.data

        # test non-existent song variant insertion
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format('000000000000000000000000'),
            content_type='application/json',
            data=json.dumps(dict(text="[verse] Test song", description="Test song")))
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # test correct song variant insertion
        rv = self.app.post(
            '/api/v1/songs/{}/variants'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(text="[verse] Test song", description="Test song")))
        assert rv.status_code == 201

        data = json.loads(rv.data)
        variant_id = data['link'].split('/')[3]

        # check get request on inserted song variant
        rv = self.app.get('/api/v1/songs/{}/variants/{}'.format(song_id, variant_id))
        assert rv.status_code == 200

        variant = json.loads(rv.data)
        assert variant['text'] == "[verse] Test song"
        assert variant['id'] == variant_id
        assert variant['description'] == "Test song"

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_put_request(self):
        # insert test song into the database
        rv = utils._post_song(self.app, title='Panic Station', description='Variant test song')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']
        variant_id = data['variants'][0]['id']

        # test wrong song variant id
        rv = utils._put_song_variant(self.app, song_id, '000000000000000000000000')
        assert rv.status_code == 404

        # test missing fields
        rv = self.app.put(
            '/api/v1/songs/{}/variants/{}'.format(song_id, variant_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data

        # test missing text field
        rv = self.app.put(
            '/api/v1/songs/{}/variants/{}'.format(song_id, variant_id),
            content_type='application/json',
            data=json.dumps(dict(description="")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "text"' in rv.data

        # test missing description field
        rv = self.app.put(
            '/api/v1/songs/{}/variants/{}'.format(song_id, variant_id),
            content_type='application/json',
            data=json.dumps(dict(text="[verse]")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "description"' in rv.data

        # test correct song variant edit request
        rv = self.app.put(
            '/api/v1/songs/{}/variants/{}'.format(song_id, variant_id),
            content_type='application/json',
            data=json.dumps(dict(text="[verse] Don't panic", description="It works")))
        assert rv.status_code == 200

        data = json.loads(rv.data)
        assert data['text'] == "[verse] Don't panic"
        assert data['description'] == "It works"

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_deletion(self):
        # insert test song into the database
        rv = utils._post_song(self.app, title='Panic Station', description='First variant')

        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

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
        variant_ids.append(data['link'].split('/')[3])

        # try to delete nonexistent song variant from the database
        rv = self.app.delete('/api/v1/songs/{}/variants/{}'.format(song_id,
                                                                   '000000000000000000000000'))
        assert rv.status_code == 404

        # delete variant of song
        rv = self.app.delete('/api/v1/songs/{}/variants/{}'.format(song_id, variant_ids[0]))
        assert rv.status_code == 204

        # check, that song is really deleted
        rv = self.app.get('/api/v1/songs/{}/variants'.format(song_id))
        data = json.loads(rv.data)
        assert len(data) == 1

        # check that variant cannot be found via its id
        rv = self.app.get('/api/v1/songs/{}/variants/{}'.format(song_id, variant_ids[0]))
        assert rv.status_code == 404
        assert b'Song variant was not found' in rv.data

        # delete second (last) variant
        rv = self.app.delete('/api/v1/songs/{}/variants/{}'.format(song_id, variant_ids[1]))
        assert rv.status_code == 204

        # check correct deletion of entire song
        rv = self.app.get('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_duplication(self):
        # insert test song into the database
        rv = utils._post_song(self.app, title='Invincible', description='Variant test song')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']
        variant_id = data['variants'][0]['id']

        # duplicate variant
        rv = self.app.get('/api/v1/songs/{}/variants/{}/duplicate'.format(song_id, variant_id))
        assert rv.status_code == 200

        # try to duplicate wrong song
        rv = self.app.get('/api/v1/songs/{}/variants/{}/duplicate'.format(
            song_id, '000000000000000000000000'))
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_permissions(self):
        # insert test song for further testing
        rv = utils._post_song(self.app, title='Bubák')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']
        variant_id = data['variants'][0]['id']

        # test wrong view permission values
        rv = utils._put_song_variant(self.app, song_id, variant_id, visibility=2)
        assert rv.status_code == 422
        assert b'"code": "wrong_value"' in rv.data
        assert b'"data": "visibility"' in rv.data

        rv = utils._put_song_variant(self.app, song_id, variant_id, visibility='abc')
        assert rv.status_code == 422
        assert b'"code": "wrong_value"' in rv.data
        assert b'"data": "visibility"' in rv.data

        # test correct permission change
        rv = utils._put_song_variant(self.app, song_id, variant_id, visibility=PERMISSION.PUBLIC)
        assert rv.status_code == 200

        # test no change
        rv = utils._put_song_variant(self.app, song_id, variant_id, visibility=PERMISSION.PUBLIC)
        assert rv.status_code == 200

        # test wrong permission change
        rv = utils._put_song_variant(self.app, song_id, variant_id, visibility=PERMISSION.PRIVATE)
        assert rv.status_code == 422
        assert b'"code": "wrong_value"' in rv.data
        assert b'"data": "visibility"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)
