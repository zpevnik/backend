import json
import unittest
import tests.utils as utils

from urllib.parse import urlsplit
from pymongo import MongoClient

from server.app import app


class InterpreterTest(unittest.TestCase):

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

    def test_interpreter_basics(self):
        # check empty database get request
        rv = self.app.get('/api/v1/interpreters')
        assert rv.status_code == 200
        assert b'[]' in rv.data

        # add interpreter into the database
        rv = utils._post_interpreter(self.app, name='Jimmy Page')
        assert rv.status_code == 201
        assert b'"link": "interpreters/' in rv.data

        # get interpreters with get request
        rv = self.app.get('/api/v1/interpreters')
        assert rv.status_code == 200

        # get id of one of interpreters
        res = json.loads(rv.data)
        interpreter_id = res[0]['id']

        # check get request on selected interpreter
        rv = self.app.get('/api/v1/interpreters/{}'.format(interpreter_id))
        assert rv.status_code == 200
        interpreter = json.loads(rv.data)
        assert interpreter['name'] == 'Jimmy Page'
        assert interpreter['id'] == interpreter_id

        # test put (edit) request
        rv = utils._put_interpreter(self.app, interpreter_id, name='Jimmy Pager')
        assert rv.status_code == 200
        interpreter = json.loads(rv.data)
        assert interpreter['name'] == 'Jimmy Pager'
        assert interpreter['id'] == interpreter_id

        # add more interpreters into the database
        rv = utils._post_interpreter(self.app, name='Jimmy Hendrix')
        rv = utils._post_interpreter(self.app, name='Eric Clapton')

        # remember size of the database
        rv = self.app.get('/api/v1/interpreters')
        res = json.loads(rv.data)
        temp = len(res)

        # delete interpreter from the database
        rv = self.app.delete('/api/v1/interpreters/{}'.format(interpreter_id))
        assert rv.status_code == 204

        # check, that interpreter is really deleted
        rv = self.app.get('/api/v1/interpreters')
        res = json.loads(rv.data)
        assert len(res) == temp - 1

        # check that interpreter cannot be found via its id
        rv = self.app.get('/api/v1/interpreters/{}'.format(interpreter_id))
        assert rv.status_code == 404
        assert b'Interpreter was not found' in rv.data

        # try to delete nonexistent interpreter from the database
        rv = self.app.delete('/api/v1/interpreters/{}'.format(interpreter_id))
        assert rv.status_code == 404

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_post_requests(self):
        # test json request error
        rv = self.app.post('/api/v1/interpreters')
        assert rv.status_code == 400

        # test missing field
        rv = self.app.post(
            '/api/v1/interpreters',
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "name"' in rv.data

        # test duplicate interpreters
        rv = utils._post_interpreter(self.app, name='Slash')
        assert rv.status_code == 201
        rv = utils._post_interpreter(self.app, name='Slash')
        assert rv.status_code == 422
        assert b'"code": "already_exists"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)

    def test_put_request(self):
        # insert test interpreter for further testing
        rv = utils._post_interpreter(self.app, name='Jack Black')
        assert rv.status_code == 201
        interpreter = json.loads(rv.data)
        interpreter_id = interpreter['link'].split('/')[1]

        # test wrong interpreter
        rv = utils._put_interpreter(self.app, '000000000000000000000000')
        assert rv.status_code == 404

        # test missing field
        rv = self.app.put(
            '/api/v1/interpreters/{}'.format(interpreter_id),
            content_type='application/json',
            data=json.dumps(dict(field="field")))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"data": "name"' in rv.data

        # clean the database
        self.mongo_client.drop_database(self.db_name)
