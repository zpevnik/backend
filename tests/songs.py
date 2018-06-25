import json
import unittest
import tests.utils as utils

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
        rv = utils._post_song(self.app, title='Back in Black')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        # get songs with get request
        rv = self.app.get('/api/v1/songs')
        assert rv.status_code == 200

        # get id of one of the songs
        res = json.loads(rv.data)
        song_id = res['data'][0]['id']

        # check get request on selected song
        rv = self.app.get('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 200
        song = json.loads(rv.data)
        assert song['title'] == 'Back in Black'
        assert song['id'] == song_id

        # test put (edit) request
        rv = utils._put_song(self.app, song_id, title='Back in White')
        assert rv.status_code == 200
        song = json.loads(rv.data)
        assert song['title'] == 'Back in White'
        assert song['id'] == song_id

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
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[],
                    variant={
                        'text': "song",
                        'description': ""
                    })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # test missing authors field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(title="Madness", interpreters=[], variant={
                    'text': "song",
                    'description': ""
                })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "authors"' in rv.data

        # test missing interpreters field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    authors={'lyrics': [],
                             'music': []},
                    variant={
                        'text': "song",
                        'description': ""
                    })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "interpreters"' in rv.data

        # test missing variant field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(title="Madness", authors={'lyrics': [],
                                               'music': []}, interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "variant"' in rv.data

        # test missing variant/text field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[],
                    variant={
                        'description': ""
                    })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "variant/text"' in rv.data

        # test missing variant/description field
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Madness",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[],
                    variant={
                        'text': "song"
                    })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "variant/description"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_put_request(self):
        # insert test song for further testing
        rv = utils._post_song(self.app, title='Panic Station')
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_id = song['id']

        # test wrong song id
        rv = utils._put_song(self.app, '000000000000000000000000', title='Panic Station')
        assert rv.status_code == 404

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
            data=json.dumps(dict(authors={'lyrics': [],
                                          'music': []}, interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "title"' in rv.data

        # test missing authors field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(title="Madness", interpreters=[])))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "authors"' in rv.data

        # test missing interpreters field
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(dict(title="Madness", authors={
                'lyrics': [],
                'music': []
            })))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "interpreters"' in rv.data

        # test correct song edit request
        rv = self.app.put(
            '/api/v1/songs/{}'.format(song_id),
            content_type='application/json',
            data=json.dumps(
                dict(title="Madness", authors={'lyrics': [],
                                               'music': []}, interpreters=[])))
        assert rv.status_code == 200

        data = json.loads(rv.data)
        assert data['title'] == "Madness"

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_song_ordering(self):
        song_ids = []

        rv = utils._post_song(self.app, title='Live and Let Die')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_ids.append(data['id'])

        rv = utils._post_song(self.app, title='Kashmir')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_ids.append(data['id'])

        rv = utils._post_song(self.app, title='Pažitka')
        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_ids.append(data['id'])

        # get sorted songs with get request
        rv = self.app.get('/api/v1/songs?order=title')
        assert rv.status_code == 200

        res = json.loads(rv.data)
        res_ids = [x['id'] for x in res['data']]

        assert res_ids[0] == song_ids[1] and res_ids[1] == song_ids[0] and res_ids[2] == song_ids[2]

        # get sorted songs with get request
        rv = self.app.get('/api/v1/songs?order=title_desc')
        assert rv.status_code == 200

        res = json.loads(rv.data)
        res_ids = [x['id'] for x in res['data']]

        assert res_ids[0] == song_ids[2] and res_ids[1] == song_ids[0] and res_ids[2] == song_ids[1]

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_authors_and_interpreters(self):
        # insert test author for further testing
        rv = utils._post_author(self.app, name='Axl Rose')
        assert rv.status_code == 201

        data = json.loads(rv.data)
        author_id = data['link'].split('/')[1]

        # insert test interpreter for further testing
        rv = utils._post_interpreter(self.app, name='Guns n Roses')
        assert rv.status_code == 201

        data = json.loads(rv.data)
        interpreter_id = data['link'].split('/')[1]

        # test wrong author insert
        rv = utils._post_song(
            self.app, title='Welcome to the Jungle', lauthors=['000000000000000000000000'])
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        rv = utils._post_song(
            self.app, title='Welcome to the Jungle', mauthors=['000000000000000000000000'])
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # test wrong interpreter insert
        rv = utils._post_song(
            self.app, title='Welcome to the Jungle', interpreters=['000000000000000000000000'])
        assert rv.status_code == 404
        assert b'"code": "does_not_exist"' in rv.data

        # test correct insert
        rv = utils._post_song(
            self.app,
            title='Welcome to the Jungle',
            lauthors=[author_id],
            mauthors=[author_id],
            interpreters=[interpreter_id])

        assert rv.status_code == 201
        assert b'"created": "' in rv.data
        assert b'"id": "' in rv.data

        data = json.loads(rv.data)
        song_id = data['id']

        # text correct song edit request
        rv = self.app.get('/api/v1/songs/{}'.format(song_id))
        assert rv.status_code == 200

        data = json.loads(rv.data)
        assert interpreter_id in data['interpreters']
        assert author_id in data['authors']['music']
        assert author_id in data['authors']['lyrics']

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_song_validation(self):
        # test nested repetition
        rv = utils._post_song(self.app, title='Kokos', text='[verse] |: |: Kulda :| :|')
        assert rv.status_code == 422
        assert b'"code": "compilation_error"' in rv.data

        # test nested repetition end before start
        rv = utils._post_song(self.app, title='Kokos', text='[verse] |: Kulda :| :|')
        assert rv.status_code == 422
        assert b'"code": "compilation_error"' in rv.data

        # test chords inside rec
        rv = utils._post_song(self.app, title='Kokos', text='[rec] Kulda [A]')
        assert rv.status_code == 422
        assert b'"code": "compilation_error"' in rv.data

        # test unknown tag
        rv = utils._post_song(self.app, title='Kokos', text='[versex]')
        assert rv.status_code == 422
        assert b'"code": "compilation_error"' in rv.data
