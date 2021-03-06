import json
import unittest

from urllib.parse import urlsplit
from bson import ObjectId
from pymongo import MongoClient

from server.app import app
from server.constants import PERMISSION


class QueryTest(unittest.TestCase):

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

    def _insert_song(self, owner, visibility, approved=False):
        # insert new song directly into database
        song_id = ObjectId()
        self.mongo_db['songs'].insert_one({
            '_id': song_id,
            'title': 'Nice song',
            'authors': {
                'lyrics': [],
                'music': []
            },
            'interpreters': [],
            'approved': approved
        })

        self.mongo_db['variants'].insert_one({
            '_id': ObjectId(),
            'song_id': song_id,
            'owner': owner,
            'title': 'Variant title',
            'text': '',
            'description': '',
            'visibility': visibility,
            'export_cache': None
        })

        return song_id

    def test_query_filtering(self):
        # create lists of ObjectIds
        validIds = []
        invalidIds = []

        #insert valid (findable) and invalid test songs into the database
        validIds.append(self._insert_song(0, PERMISSION.PRIVATE))
        validIds.append(self._insert_song(0, PERMISSION.PUBLIC))

        validIds.append(self._insert_song(0, PERMISSION.PRIVATE, True))
        validIds.append(self._insert_song(0, PERMISSION.PUBLIC, True))

        invalidIds.append(self._insert_song(1, PERMISSION.PRIVATE))
        validIds.append(self._insert_song(1, PERMISSION.PUBLIC))

        invalidIds.append(self._insert_song(1, PERMISSION.PRIVATE, True))
        validIds.append(self._insert_song(1, PERMISSION.PUBLIC, True))

        invalidIds.append(self._insert_song(1, PERMISSION.PRIVATE))
        # this is a temporal change as approved var should affect visibility
        validIds.append(self._insert_song(1, PERMISSION.PUBLIC))

        invalidIds.append(self._insert_song(1, PERMISSION.PRIVATE, True))
        validIds.append(self._insert_song(1, PERMISSION.PUBLIC, True))

        #query server for all inserted songs
        rv = self.app.get('/api/v1/songs?per_page=100')
        res = json.loads(rv.data)

        assert rv.status_code == 200
        assert int(res['count']) == len(validIds)

        # check that correct songs were returned
        Ids = [ObjectId(x['id']) for x in res['data']]

        for _id in Ids:
            assert _id in validIds

        # clean the database
        self.mongo_client.drop_database(self.db_name)
