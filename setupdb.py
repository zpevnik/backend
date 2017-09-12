#!./venv/bin/python3.6

"""Module for correct database key creation"""

import os
import pymongo

from urllib.parse import urlsplit

from server.config import MONGODB_URI


def setup_database():
    # get database address from config file
    mongo_address = MONGODB_URI

    # get unit test database if we are unit testing
    if os.getenv('ZPEVNIK_UNITTEST', False):
        mongo_address = os.getenv('ZPEVNIK_UNITTEST')

    # setup database connecion
    mongo_client = pymongo.MongoClient(mongo_address)
    parsed = urlsplit(mongo_address)
    db = mongo_client[parsed.path[1:]]

    # remove all indexes
    db['songbooks'].drop_indexes()
    db['songs'].drop_indexes()

    # prepare songbooks database indexes
    db['songbooks'].create_index([("title", pymongo.TEXT)], name="SongbookIndex")

    # prepare songs database indexes
    db['songs'].create_index([("title", pymongo.TEXT),
                              ("text", pymongo.TEXT)],
                             name="SongIndex",
                             weights={"title": 3})

    print('Done!')

setup_database()
