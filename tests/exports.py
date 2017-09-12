import os
import json
import unittest

from pymongo import MongoClient


class ExportTest(unittest.TestCase):

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

        # delete generated file
        filename = str(rv.data).split('/')[1][:-1]
        os.remove(os.path.join('./songs/done', filename))

        # clean the database
        self.mongo_client.drop_database('unittest')
