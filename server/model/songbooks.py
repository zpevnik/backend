from flask import g
from datetime import datetime

from server.util import generate_random_uuid, uuid_from_str, uuid_to_str
from server.util.exceptions import AppException

import logging
logger = logging.getLogger(__name__)

class Songbooks(object):
    """Collection for managing CRUD operation in database for songs

    Args:
      model (server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'songs'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_song(self, data):
        """Create new song instance and insert it into database.

        Args:
          data (dict): Data about the song (title, authors and text).

        Returns:
          Song: Instance of the new song.
        """
        song = Song({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'title': data['title'],
            'text': data['text'],
            'authors': data['authors'] if 'authors' in data else ''
        })
        self._collection.insert(song.serialize())

        return song

    def save(self, song):
        """Save instance of song into database.

        Args:
          song (Song): instance of the song.
        """
        self._collection.update(
            {'_id': uuid_from_str(song.get_id())},
            {'$set': song.serialize(update=True)}
        )

    def find(self):
        """Find all the songs satisfying given restrictions 
        (currently no restrictions).

        Returns:
          list: List of song instances or None.
        """
        doc = self._collection.find({})

        if doc.count() == 0:
            return []

        songs = []
        for song in doc:
            songs.append(Song(song))

        return songs


class Songbook(object):
    """Class for song abstraction.

    Args:
      song (dict): Island dictionary.

    Attributes:
      _id (str): Island UUID.
      _created (str): Timestamp of the island creation.
      _authors (str): Authors...
      _title (str): Title of the song.
      _text (str): Lyrics and chords of the song.
    """

    def __init__(self, song):
        self._id = uuid_to_str(song['_id'])
        self._created = song['created']
        self._authors = song['authors']
        self._title = song['title']
        self._text = song['text']

    def serialize(self, update=False):
        song = {
            'authors': self._authors,
            'title': self._title,
            'text': self._text
        }

        if not update:
            song['_id'] = uuid_from_str(self._id)
            song['created'] = self._created

        return song

    def get_id(self):
        return self._id

    def generate_tex(self, filename):
        with open('songs/sample/sample.sbd', 'r') as file:
            filedata = file.read()

        # todo translate song
        with open('test.song', 'r') as file:
            song = file.read()

        filedata = filedata.replace('$title$', self._title)
        filedata = filedata.replace('$authors$', self._authors )
        filedata = filedata.replace('$song$', song)

        with open('songs/temp/' + filename + '.sbd', 'a') as file:
            file.write(filedata)


    def __repr__(self):
        return '<%r id=%r title=%r authors=%r>' % (self.__class__.__name__, self._id, self._title, self._authors)
