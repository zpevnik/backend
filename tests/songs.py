import json
import unittest

from urllib.parse import urlsplit
from pymongo import MongoClient

from server.app import app


class SongTest(unittest.TestCase):

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

    def test_song_basics(self):
        # check empty database get request
        rv = self.app.get('/api/v1/songs')
        assert rv.status_code == 200
        assert b'[]' in rv.data

        # add song into the database
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Back in Black",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 201
        assert b'"link": "songs/' in rv.data

        # get songs with get request
        rv = self.app.get('/api/v1/songs')
        assert rv.status_code == 200

        # get id of one of the songs
        res = json.loads(rv.data)
        song_id = res[0]['id']

        # check get request on selected song
        rv = self.app.get('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 200
        song = json.loads(rv.data)
        assert song['title'] == 'Back in Black'
        assert song['id'] == song_id

        # test put (edit) request
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Back in White",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 200
        song = json.loads(rv.data)
        assert song['title'] == 'Back in White'
        assert song['id'] == song_id

        # add more songs into the database
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Map of Problematique",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Bliss",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))

        # remember size of the database
        rv = self.app.get('/api/v1/songs')
        res = json.loads(rv.data)
        temp = len(res)

        # delete song from the database
        rv = self.app.delete('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 204

        # check, that song is really deleted
        rv = self.app.get('/api/v1/songs')
        res = json.loads(rv.data)
        assert len(res) == temp - 1

        # check that song cannot be found via its id
        rv = self.app.get('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 422
        assert b'Song was not found' in rv.data

        # try to delete nonexistent song from the database
        rv = self.app.delete('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 422

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_post_requests(self):
        # test json request error
        rv = self.app.post('/api/v1/songs')
        assert rv.status_code == 400

        # test missing fields
        rv = self.app.post(
            '/api/v1/songs', content_type='application/json', data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data

        # test missing title field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "title"' in rv.data

        # test missing text field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "text"' in rv.data

        # test missing description field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    text="song",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "description"' in rv.data

        # test missing authors field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(dict(title="Madness", text="song", description="", interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "authors"' in rv.data

        # test missing interpreters field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []})))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "interpreters"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_put_request(self):
        # insert test song for further testing
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Panic Station",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_id = song['link'].split('/')[1]

        # test wrong song id
        rv = self.app.put(
            '/api/v1/songs/{}'.format('000000000000000000000000'),
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Panic Station",
                    text="song",
                    description="this song is pretty awesome",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422

        # test missing fields
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data

        # test missing title field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "title"' in rv.data

        # test missing text field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "text"' in rv.data

        # test missing description field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    text="song",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "description"' in rv.data

        # test missing authors field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(title="Madness", text="song", description="", interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "authors"' in rv.data

        # test missing interpreters field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []})))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "interpreters"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_authors_and_interpreters(self):
        # insert test author for further testing
        rv = self.app.post(
            '/api/v1/authors',
            content_type='application/json',
            data=json.dumps(dict(name='Axl Rose')))
        assert rv.status_code == 201
        author = json.loads(rv.data)
        author_id = author['link'].split('/')[1]

        # insert test interpreter for further testing
        rv = self.app.post(
            '/api/v1/interpreters',
            content_type='application/json',
            data=json.dumps(dict(name='Axl Rose')))
        assert rv.status_code == 201
        interpreter = json.loads(rv.data)
        interpreter_id = interpreter['link'].split('/')[1]

        # test wrong author insert
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Welcome to the Jungle",
                    text="song",
                    description="",
                    authors={'lyrics': ['000000000000000000000000'],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"message": "Author was not found."' in rv.data

        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Welcome to the Jungle",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': ['000000000000000000000000']},
                    interpreters=[])))
        assert rv.status_code == 422
        assert b'"message": "Author was not found."' in rv.data

        # test wrong interpreter insert
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Welcome to the Jungle",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=['000000000000000000000000'])))
        assert rv.status_code == 422
        assert b'"message": "Interpreter was not found."' in rv.data

        # test correct insert
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Welcome to the Jungle",
                    text="song",
                    description="",
                    authors={'lyrics': [author_id],
                             'music': [author_id]},
                    interpreters=[interpreter_id])))
        assert rv.status_code == 201
        assert b'"link": "songs/' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_duplication(self):
        # insert test song for further testing
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Invincible",
                    text="song",
                    description="",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_id = song['link'].split('/')[1]

        # duplicate song
        rv = self.app.get('/api/v1/songs/duplicate/{}'.format(song_id))
        assert rv.status_code == 201
        assert b'"link": "songs/' in rv.data

        # try to duplicate wrong song
        rv = self.app.get('/api/v1/songs/duplicate/{}'.format('000000000000000000000000'))
        assert rv.status_code == 422
        assert b'"message": "Song was not found."' in rv.data
