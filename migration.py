#!./__venv__/bin/python3.6

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


def reset_variant_cache():
    collection = db['variants']
    variants = collection.find()

    for variant in variants:
        if not variant['export_cache']:
            continue

        variant['export_cache'] = None
        collection.update_one({'_id': variant['_id']}, {'$set': variant})


def migration_2018_18_04_1():
    logger.info('18.04.2018 - Renaming songbook option size to format.')

    reset_variant_cache()

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        options = songbook['options']
        if 'format' in songbook['options']:
            continue

        songbook['options']['format'] = songbook['options']['size']
        del songbook['options']['size']

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2018_12_04_1():
    logger.info('12.04.2018 - Adding editor key to users.')

    collection = db['users']
    users = collection.find()

    for user in users:
        if 'editor' in user:
            continue

        user['editor'] = False

        collection.update_one({'_id': user['_id']}, {'$set': user})
        collection.update_one({'_id': user['_id']}, {'$unset': {'unit': ''}})


def migration_2018_11_04_1():
    logger.info('11.04.2018 - Migrating songs into new variant concept.')

    song_collection = db['songs']
    variant_collection = db['variants']
    songbooks_collection = db['songbooks']

    song_map = {}

    songs = song_collection.find()
    for song in songs:
        if 'text' not in song:
            continue

        # create new variant for given song
        variant_id = ObjectId()
        variant_collection.insert_one({
            '_id': variant_id,
            'song_id': song['_id'],
            'owner': song['owner'],
            'text': song['text'],
            'description': song['description'],
            'visibility': song['visibility'],
            'export_cache': None
        })

        # map variant to its song
        song_map[str(song['_id'])] = variant_id

        # remove variant stuff from the song
        song_collection.update_one({'_id': song['_id']}, {'$unset': {'text': ''}})
        song_collection.update_one({'_id': song['_id']}, {'$unset': {'owner': ''}})
        song_collection.update_one({'_id': song['_id']}, {'$unset': {'description': ''}})
        song_collection.update_one({'_id': song['_id']}, {'$unset': {'visibility': ''}})
        song_collection.update_one({'_id': song['_id']}, {'$unset': {'export_cache': ''}})

    # update songbooks with variants
    songbooks = songbooks_collection.find()
    for songbook in songbooks:
        for song in songbook['songs']:
            if 'variant_id' in song:
                continue

            song['variant_id'] = str(song_map[song['id']])
            del song['id']

        songbooks_collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2018_07_04_1():
    logger.info('07.04.2018 - Removing unused keys for permissions from songbooks.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if 'owner_unit' not in songbook:
            continue

        collection.update_one({'_id': songbook['_id']}, {'$unset': {'owner_unit': ''}})


def migration_2018_07_04_2():
    logger.info('07.04.2018 - Removing unused keys for permissions from songs.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        if 'owner_unit' in song:
            collection.update_one({'_id': song['_id']}, {'$unset': {'owner_unit': ''}})

        if 'edit_perm' in song:
            collection.update_one({'_id': song['_id']}, {'$unset': {'edit_perm': ''}})


def migration_2018_07_04_3():
    logger.info('07.04.2018 - Migrate echo tags to rec.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        song['text'] = song['text'].replace('[echo]', '[rec]')

        collection.update_one({'_id': song['_id']}, {'$set': song})


def migration_2018_07_04_4():
    logger.info('07.04.2018 - Changed old public permissions to new ones.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        if song['visibility'] == 2:

            song['visibility'] = 1
            collection.update_one({'_id': song['_id']}, {'$set': song})


def migration_2018_03_02_1():
    logger.info('02.03.2018 - Removing active songbook entry from user.')

    collection = db['users']
    users = collection.find()

    for user in users:
        if 'active_songbook' not in user:
            continue

        collection.update_one({'_id': user['_id']}, {'$unset': {'active_songbook': ''}})


def migration_2018_03_12_1():
    logger.info('12.03.2018 - Adding song_numbering option to songbooks.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if 'song_numbering' in songbook['options']:
            continue

        songbook['options']['song_numbering'] = False

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2018_12_22_1():
    logger.info('22.12.2017 - Migrating songs in songbook to new struct.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if isinstance(songbook['songs'], list):
            continue

        songbook['songs'] = [item for item in songbook['songs'].values()]

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2017_12_07_1():
    logger.info('07.12.2017 - Migrating permission values in songs.')

    collection = db['songs']
    songs = collection.find()

    for song in songs:
        if 'approved' in song:
            continue

        if song['visibility'] == 'private':
            song['visibility'] = int(PERMISSION.PRIVATE)
        #elif song['visibility'] == 'unit':
        #    song['visibility'] = int(PERMISSION.UNIT)
        elif song['visibility'] == 'public':
            song['visibility'] = int(PERMISSION.PUBLIC)

        if song['edit_perm'] == 'private':
            song['edit_perm'] = int(PERMISSION.PRIVATE)
        #elif song['edit_perm'] == 'unit':
        #    song['edit_perm'] = int(PERMISSION.UNIT)
        elif song['edit_perm'] == 'public':
            song['edit_perm'] = int(PERMISSION.PUBLIC)

        song['approved'] = False

        collection.update_one({'_id': song['_id']}, {'$set': song})


def migration_2017_12_07_2():
    logger.info('07.12.2017 - Removing unused fields in songbooks.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if 'visibility' not in songbook:
            continue

        collection.update_one({'_id': songbook['_id']}, {'$unset': {'visibility': ''}})
        collection.update_one({'_id': songbook['_id']}, {'$unset': {'edit_perm': ''}})


def migration_2017_10_04_1():
    logger.info('04.10.2017 - Adding songbook cache.')

    collection = db['songbooks']
    songbooks = collection.find()

    for songbook in songbooks:
        if 'cached_file' in songbook:
            continue
        songbook['cached_file'] = None
        songbook['cache_expiration'] = None

        collection.update_one({'_id': songbook['_id']}, {'$set': songbook})


def migration_2017_09_26_1():
    logger.info('26.09.2017 - Adding options to songbooks.')

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
    logger.info('12.09.2017 - Adding export cache to songs.')

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
#migration_2017_10_04_1()

#migration_2017_12_07_1()
#migration_2017_12_07_2()
#migration_2018_12_22_1()
#migration_2018_03_02_1()
#migration_2018_07_04_1()
#migration_2018_07_04_2()
#migration_2018_07_04_3()
#migration_2018_07_04_4()
#migration_2018_11_04_1()
#migration_2018_12_04_1()

migration_2018_18_04_1()
