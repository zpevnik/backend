#!./venv/bin/python3.6

import logging

from flask import Flask
from pymongo import MongoClient
from urllib.parse import urlsplit

from server.model import Model
from server.constants import PERMISSION


logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_pyfile('server/config.py')

parsed = urlsplit(app.config['MONGODB_URI'])
mongoClient = MongoClient(app.config['MONGODB_URI'])
db = mongoClient[parsed.path[1:]]

# Authenticate
if '@' in app.config['MONGODB_URI']:
    user, password = parsed.netloc.split('@')[0].split(':')
    db.authenticate(user, password)

model = Model(db=db)


def migration_2017_08_18_1():
    logger.info('12.08.2017 - Changing authors database to Zpevnik version 2.')

    collection = db['authors']
    authors = collection.find()

    for author in authors:
        if 'name' in author:
            continue

        if author['surname']:
            author['name'] = "{} {}".format(author['firstname'], author['surname']).strip()
        else:
            author['name'] = author['firstname']

        collection.update(
            {'_id': author['_id']},
            {'$set': author}
        )

        collection.update(
            {'_id': author['_id']},
            {'$unset': {
                'firstname': '',
                'surname': ''
            }}
        )

def migration_2017_08_18_2():
    logger.info('12.08.2017 - Changing songbooks database to Zpevnik version 2.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        songbook['owner'] = None if 'owner' not in songbook else songbook['owner']
        songbook['owner_unit'] = None if 'owner_unit' not in songbook else songbook['owner_unit']
        songbook['visibility'] = PERMISSION.PUBLIC if 'visibility' not in songbook else songbook['visibility']
        songbook['edit_perm'] = PERMISSION.PUBLIC if 'edit_perm' not in songbook else songbook['edit_perm']

        collection.update(
            {'_id': songbook['_id']},
            {'$set': songbook}
        )

def migration_2017_08_18_3():
    logger.info('12.08.2017 - Changing users database to Zpevnik version 2.')

    collection = db['users']
    users = collection.find()

    for user in users:
        user['active_songbook'] = None if 'active_songbook' not in user else user['active_songbook']
        user['last_login'] = user['lastLogin'] if 'last_login' not in user else user['last_login']

        collection.update(
            {'_id': user['_id']},
            {'$set': user}
        )

        collection.update(
            {'_id': user['_id']},
            {'$unset': {
                'lastLogin': ''
            }}
        )

def migration_2017_08_18_4():
    logger.info('12.08.2017 - Changing songs database to Zpevnik version 2.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        song['owner'] = None if 'owner' not in song else song['owner']
        song['owner_unit'] = None if 'owner_unit' not in song else song['owner_unit']
        song['description'] = '' if 'description' not in song else song['description']
        song['visibility'] = PERMISSION.PUBLIC if 'visibility' not in song else song['visibility']
        song['edit_perm'] = PERMISSION.PUBLIC if 'edit_perm' not in song else song['edit_perm']

        collection.update(
            {'_id': song['_id']},
            {'$set': song}
        )

#migration_2017_08_18_1()
#migration_2017_08_18_2()
#migration_2017_08_18_3()
#migration_2017_08_18_4()
