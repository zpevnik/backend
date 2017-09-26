#!./venv/bin/python3.6

import time
import random
import logging

from flask import Flask
from pymongo import MongoClient
from urllib.parse import urlsplit

from bson import ObjectId

from server.model import Model
from server.constants import OPTIONS
from server.constants import PERMISSION

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_pyfile('server/config.py')

parsed = urlsplit(app.config['MONGODB_URI'])
mongo_client = MongoClient(app.config['MONGODB_URI'])
db = mongo_client[parsed.path[1:]]

model = Model(db=db)


def migration_2017_09_26_1():
    logger.info('12.08.2017 - Adding options to songbooks.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if 'options' in songbook:
            continue
        songbook['options'] = {
            'size': OPTIONS.SIZE.A4,
            'columns': 2,
            'index': True,
            'chorded': True,
            'front_index': False,
            'page_numbering': True
        }

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2017_09_12_1():
    logger.info('12.08.2017 - Adding export cache to songs.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        if 'export_cache' in song:
            continue
        song['export_cache'] = None

        collection.update_one({'_id': song['_id']}, {'$set': song})


def migration_2017_09_05_2():
    logger.info('05.09.2017 - Updating songs to new text format.')

    def translate(text):
        state_chorus = False
        state_verse = False
        output = ""

        def finish_part(state_chorus, state_verse):
            return "[chorus]\n" if state_chorus else \
                   "[verse]\n" if state_verse else \
                   ""

        content = [x.strip() for x in text.split('\n')]

        for line in content:
            if line == "##":
                output += finish_part(state_chorus, state_verse)
                state_chorus = False
                state_verse = True
                output += "[verse]"

            elif line == "**":
                output += finish_part(state_chorus, state_verse)
                state_verse = False
                state_chorus = True
                output += "[chorus]"

            elif line == "***":
                output += finish_part(state_chorus, state_verse)
                state_verse = False
                state_chorus = False
                output += "[chorus][chorus]\n"

            else:
                line = line.replace('>', '[echo]')
                line = line.replace('<', '[echo]\n')
                line = line.replace('||', '[repetition]\n')
                line = line.replace('|', '[repetition]')
                output += line + "\n"

        return output

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        if not song['text']:
            continue

        song['text'] = translate(song['text'])
        collection.update_one({'_id': song['_id']}, {'$set': song})


def migration_2017_09_05_1():
    logger.info('05.09.2017 - Updating databse to ObjectId & splitting Authors and Interpreters.')

    # laod everything into the memory
    songs = db['songs'].find()
    authors = db['authors'].find()

    # map all authors to new keys and reinsert them into the database
    authormap = {}
    for author in authors:
        if 'created' not in author:
            continue

        temp = hex(int(author['created'].timestamp()))[2:]
        temp += '0000000000'
        temp += ''.join(random.choice('0123456789abcdef') for n in range(6))

        authormap[author['_id'].hex] = temp
        author['_id'] = ObjectId(temp)
        author.pop('created', None)

        db['authors'].insert_one(author)
        db['interpreters'].insert_one(author)

    for song in songs:
        if 'created' not in song:
            continue

        temp = hex(int(song['created'].timestamp()))[2:]
        temp += '0000000000'
        temp += ''.join(random.choice('0123456789abcdef') for n in range(6))

        song['_id'] = ObjectId(temp)
        song.pop('created', None)

        # get all interpreters and authors
        interpreters = song['interpreters']
        mauthors = song['authors']['music']
        lauthors = song['authors']['lyrics']

        # clean author and interpreter arrays
        song['interpreters'] = []
        song['authors'] = {'music': [], 'lyrics': []}

        # insert new mapped values
        for interpreter in interpreters:
            key = authormap[interpreter]
            song['interpreters'].append(key)
        for author in mauthors:
            key = authormap[author]
            song['authors']['music'].append(key)
        for author in lauthors:
            key = authormap[author]
            song['authors']['lyrics'].append(key)

        db['songs'].insert_one(song)

    # clean old database entries
    db['authors'].delete_many({'created': {'$exists': True}})
    db['songs'].delete_many({'created': {'$exists': True}})


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

        collection.update_one({'_id': author['_id']}, {'$set': author})

        collection.update_one({'_id': author['_id']}, {'$unset': {'firstname': '', 'surname': ''}})


def migration_2017_08_18_2():
    logger.info('12.08.2017 - Changing songbooks database to Zpevnik version 2.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        songbook['owner'] = None if 'owner' not in songbook else songbook['owner']
        songbook['owner_unit'] = None if 'owner_unit' not in songbook else songbook['owner_unit']
        songbook['visibility'] = PERMISSION.PUBLIC if 'visibility' not in songbook else songbook[
            'visibility']
        songbook['edit_perm'] = PERMISSION.PUBLIC if 'edit_perm' not in songbook else songbook[
            'edit_perm']

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2017_08_18_3():
    logger.info('12.08.2017 - Changing users database to Zpevnik version 2.')

    collection = db['users']
    users = collection.find()

    for user in users:
        user['active_songbook'] = None if 'active_songbook' not in user else user['active_songbook']
        user['last_login'] = user['lastLogin'] if 'last_login' not in user else user['last_login']

        collection.update_one({'_id': user['_id']}, {'$set': user})

        collection.update_one({'_id': user['_id']}, {'$unset': {'lastLogin': ''}})


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

        collection.update_one({'_id': song['_id']}, {'$set': song})


#migration_2017_08_18_1()
#migration_2017_08_18_2()
#migration_2017_08_18_3()
#migration_2017_08_18_4()

#migration_2017_09_05_1()
#migration_2017_09_05_2()

#migration_2017_09_12_1()

#migration_2017_09_26_1()
