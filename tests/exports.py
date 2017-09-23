import os
import json
import unittest

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

    def test_song_export(self):
        # add test song into the database
        rv = self.app.post(
            '/api/v1/songs',
            content_type='application/json',
            data=json.dumps(
                dict(
                    title="Nights In White Satin",
                    text="[verse][Em]Nights in white [D]satin, [Em]never reaching the [D]end,\n"
                    "[C]Letters I've [G]written, [F]never meaning to [Em]send.\n"
                    "[Em]Beauty I've [D]always missed, [Em]with these eyes be[D]fore,\n"
                    "[C]Just what the [G]truth is, [F] I can't say any[Em]more.\n"
                    "[verse]",
                    description="This is a test song",
                    authors={'lyrics': [],
                             'music': []},
                    interpreters=[])))
        assert rv.status_code == 201
        song = json.loads(rv.data)
        song_id = song['link'].split('/')[1]

        # export test song as pdf
        rv = self.app.get('/api/v1/songs/{}'.format(song_id), content_type='application/pdf')
        assert rv.status_code == 200
        assert b'download/' in rv.data

        # check correct json structure
        data = json.loads(rv.data)
        assert 'link' in data
        assert 'log' in data

        # delete generated file
        filename = str(data['link']).split('/')[1]
        os.remove(os.path.join('./songs/done', filename))

        # clean the database
        self.mongo_client.drop_database('unittest')
