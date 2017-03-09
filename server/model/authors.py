from flask import g
from datetime import datetime

from server.util import generate_random_uuid, uuid_from_str, uuid_to_str
from server.util.exceptions import AppException

import logging
logger = logging.getLogger(__name__)

class Authors(object):
    """Collection for managing CRUD operation in database for authors

    Args:
      model (server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'authors'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_author(self, data):
        """Create new author instance and insert it into database.

        Args:
          data (dict): Data about the author (name, surname).

        Returns:
          Author: Instance of the new author.
        """
        author = Author({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'firstname': data['firstname'],
            'surname': data['surname']
        })
        self._collection.insert(author.serialize())

        return author

    def save(self, author):
        """Save instance of author into database.

        Args:
          author (Author): instance of the author.
        """
        self._collection.update(
            {'_id': uuid_from_str(author.get_id())},
            {'$set': author.serialize(update=True)}
        )

    def find(self):
        """Find all the authors satisfying given restrictions 
        (currently no restrictions).

        Returns:
          list: List of authors instances or None.
        """
        doc = self._collection.find({})

        if doc.count() == 0:
            return []

        authors = []
        for author in doc:
            authors.append(Author(author))

        return authors


class Author(object):
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

    def __repr__(self):
        return '<%r id=%r title=%r authors=%r>' % (self.__class__.__name__, self._id, self._title, self._authors)
