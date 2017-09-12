import os
import json
import unittest

from pymongo import MongoClient


class InterpreterTest(unittest.TestCase):
    def setUp(self):
        # enable testing environment
        os.environ['ZPEVNIK_UNITTEST'] = 'mongodb://localhost:27017/unittest'

        # get application for testing
        from server.app import app
        self.app = app.test_client()

        # login into the application via test login endpoint
        self.app.get('/test_login')

    def tearDown(self):
        # disable testing environment
        del os.environ['ZPEVNIK_UNITTEST']

        # delete all test database entries
        mongoClient = MongoClient('mongodb://localhost:27017/unittest')
        mongoClient.drop_database('unittest')

    def test_interpreter_basics(self):
        # check empty database get request
        rv = self.app.get('/api/v1/interpreters')
        assert rv.status_code == 200
        assert b'[]' in rv.data

        # add interpreter into the database
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Jimmy Page'
                           )))
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
        rv = self.app.put('/api/v1/interpreters/{}'.format(interpreter_id),
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Jimmy Pager'
                           )))
        assert rv.status_code == 200
        interpreter = json.loads(rv.data)
        assert interpreter['name'] == 'Jimmy Pager'
        assert interpreter['id'] == interpreter_id

        # add more interpreters into the database
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Jimmy Hendrix'
                           )))
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Eric Clapton'
                           )))

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
        assert rv.status_code == 422
        assert b'Interpreter was not found' in rv.data

        # try to delete nonexistent interpreter from the database
        rv = self.app.delete('/api/v1/interpreters/{}'.format(interpreter_id))
        assert rv.status_code == 422

    def test_post_requests(self):
        # test json request error
        rv = self.app.post('/api/v1/interpreters')
        assert rv.status_code == 400

        # test missing field
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               field="field"
                           )))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "name"' in rv.data

        # test duplicate interpreters
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Slash'
                           )))
        assert rv.status_code == 201
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Slash'
                           )))
        assert rv.status_code == 422
        assert b'"code": "already_exists"' in rv.data

    def test_put_request(self):
        # insert test interpreter for further testing
        rv = self.app.post('/api/v1/interpreters',
                           content_type='application/json',
                           data=json.dumps(dict(
                               name='Jack Black'
                           )))
        assert rv.status_code == 201
        interpreter = json.loads(rv.data)
        interpreter_id = interpreter['link'].split('/')[1]

        # test wrong interpreter
        rv = self.app.put('/api/v1/interpreters/{}'.format('000000000000000000000000'),
                           content_type='application/json',
                           data=json.dumps(dict(
                               field="field"
                           )))
        assert rv.status_code == 422

        # test missing field
        rv = self.app.put('/api/v1/interpreters/{}'.format(interpreter_id),
                           content_type='application/json',
                           data=json.dumps(dict(
                               field="field"
                           )))
        assert rv.status_code == 422
        assert b'"code": "missing_field"' in rv.data
        assert b'"field": "name"' in rv.data
