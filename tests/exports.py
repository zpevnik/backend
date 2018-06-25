import os
import json
import unittest
import tests.utils as utils

from urllib.parse import urlsplit
from pymongo import MongoClient

from server.app import app


class ExportTest(unittest.TestCase):

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

    def test_songbook_export(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title="Linkin Park songbook")
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['id']

        # insert test songs for further testing
        variant_ids = []
        rv = utils._post_song(
            self.app,
            title="Numb",
            text="[verse][F#m]I'm tired of being what you [D]want me to be\n"
            "[A]Feeling so faithless\n"
            "Lost [E]under the surface\n"
            "[F#m]I don't know what you're ex[D]pecting of me\n"
            "[A]Put under the pressure\n"
            "of [E]walking in your [D]shoes\n"
            "[rec]Caught in the undertow, just caught in the undertow\n")
        assert rv.status_code == 201
        song = json.loads(rv.data)
        variant_ids.append(song['variants'][0]['id'])

        rv = utils._post_song(
            self.app,
            title="Given Up",
            text="[verse][Em]Wake in a sweat again\n"
            "[G]Another day's been laid to [C]waste\n"
            "In my dis[D]grace\n"
            "[Em]Stuck in my head again\n"
            "[G]Feels like I'll never leave this [C]place\n"
            "There's no es[D]cape\n"
            "I'm my [Em]own worst [G]ene[C]my\n")
        assert rv.status_code == 201
        song = json.loads(rv.data)
        variant_ids.append(song['variants'][0]['id'])

        # get current songbook
        rv = self.app.get('/api/v1/songbooks/{}'.format(songbook_id))
        songbook = json.loads(rv.data)

        # insert songs into the songbook
        songbook['songs'] = [{'variant_id': variant_ids[0]}, {'variant_id': variant_ids[1]}]
        rv = self.app.put(
            '/api/v1/songbooks/{}/songs'.format(songbook_id),
            content_type='application/json',
            data=json.dumps(songbook))
        assert rv.status_code == 200

        # export test songbook as pdf
        rv = self.app.get(
            '/api/v1/songbooks/{}'.format(songbook_id), headers={
                'Accept': 'application/pdf'
            })
        assert rv.status_code == 200
        assert b'download/' in rv.data

        # check correct json structure
        data = json.loads(rv.data)
        assert 'link' in data

        # delete generated file
        link = json.loads(rv.data)['link']
        filename = str(link).split('/')[1]
        os.remove(os.path.join('./songs/done', filename))

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_songbook_export_cache(self):
        # insert test songbook for further testing
        rv = utils._post_songbook(self.app, title="Cache songbook")
        assert rv.status_code == 201
        songbook = json.loads(rv.data)
        songbook_id = songbook['id']

        # export test songbook as pdf
        rv = self.app.get(
            '/api/v1/songbooks/{}'.format(songbook_id), headers={
                'Accept': 'application/pdf'
            })
        assert rv.status_code == 200
        assert b'download/' in rv.data

        first_link = json.loads(rv.data)['link']

        # test export cache
        rv = self.app.get(
            '/api/v1/songbooks/{}'.format(songbook_id), headers={
                'Accept': 'application/pdf'
            })
        assert rv.status_code == 200
        assert b'download/' in rv.data

        second_link = json.loads(rv.data)['link']
        assert first_link == second_link

        # delete generated file
        filename = str(first_link).split('/')[1]
        os.remove(os.path.join('./songs/done', filename))

        # clean the database
        self.mongo_client.drop_database(self.db_name)
