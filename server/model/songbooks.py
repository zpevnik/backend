from flask import g
from datetime import datetime

from server.util import generate_random_uuid, uuid_from_str, uuid_to_str
from server.util.exceptions import AppException

import logging
logger = logging.getLogger(__name__)

class Songbooks(object):
    """Collection for managing CRUD operation in database for songbooks

    Args:
      model (server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'songbooks'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_songbook(self, data):
        """Create new songbook instance and insert it into database.

        Args:
          data (dict): Data about the songbook (title).

        Returns:
          Songbook: Instance of the new songbook.
        """
        songbook = Songbook({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'title': data['title'],
            'songs': []
        })
        self._collection.insert(songbook.serialize())

        return songbook

    def save(self, songbook):
        """Save instance of songbook into database.

        Args:
          songbook (Songbook): instance of the songbook.
        """
        self._collection.update(
            {'_id': uuid_from_str(songbook.get_id())},
            {'$set': songbook.serialize(update=True)}
        )

    def find(self):
        """Find all the songbooks satisfying given restrictions 
        (currently no restrictions).

        Returns:
          list: List of songbook instances or None.
        """
        doc = self._collection.find({})

        if doc.count() == 0:
            return []

        songbooks = []
        for songbook in doc:
            songbooks.append(Songbook(songbook))

        return songbooks


class Songbook(object):

    def __init__(self, songbook):
        self._id = uuid_to_str(songbook['_id'])
        self._created = songbook['created']
        self._title = songbook['title']
        self._songs = songbook['songs']

    def serialize(self, update=False):
        songbook = {
            'title': self._title,
            'songs': self._songs
        }

        if not update:
            songbook['_id'] = uuid_from_str(self._id)
            songbook['created'] = self._created

        return songbook

    def get_serialized_data(self):
        songs = []
        # TODO
        #songs_doc = g.model.songs.find_by_account_id(self._active_account)
        #for song in songs_doc:
        #    songs.append(song.get_serialized_data())

        return {
            'id': self._id,
            'created': self._created.isoformat(),
            'title': self._title,
            'songs': songs
        }

    def get_id(self):
        return self._id


    def __repr__(self):
        return '<%r id=%r title=%r authors=%r>' % (self.__class__.__name__, self._id, self._title, self._authors)
