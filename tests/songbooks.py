import unittest

from urllib.parse import urlsplit
from bson import ObjectId
from pymongo import MongoClient

from server.app import app
from server.constants import PERMISSION


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

    def test_active_songbook(self):
        # create songbooks for testing purposes
        # test user owned songbook
        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 0,
            'owner_unit': 0,
            'visibility': PERMISSION.PRIVATE,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
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
            'visibility': PERMISSION.PRIVATE,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 0,
            'visibility': PERMISSION.UNIT,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 0,
            'visibility': PERMISSION.UNIT,
            'edit_perm': PERMISSION.UNIT,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 200

        # test other songbooks
        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.PRIVATE,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.UNIT,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.PUBLIC,
            'edit_perm': PERMISSION.PRIVATE,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.UNIT,
            'edit_perm': PERMISSION.UNIT,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.PUBLIC,
            'edit_perm': PERMISSION.UNIT,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 404

        songbook_id = ObjectId()
        self.mongo_db['songbooks'].insert_one({
            '_id': songbook_id,
            'title': 'My songbook',
            'owner': 1,
            'owner_unit': 1,
            'visibility': PERMISSION.PUBLIC,
            'edit_perm': PERMISSION.PUBLIC,
            'songs': {}
        })
        rv = self.app.put('/api/v1/users/songbook/{}'.format(songbook_id))
        assert rv.status_code == 200

    # TODO
    def test_something(self):
        pass
