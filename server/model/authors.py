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

    def delete(self, author):
        """Delete author from the database.

        Args:
          author (Author): instance of the author.
        """
        self._collection.delete_one(
            {'_id': uuid_from_str(author.get_id())}
        )

    def find_special(self, query, page, per_page):
        doc = self._collection.find({'$text':{'$search': query}},
                                    {'score': {'$meta': "textScore"}}) \
                                    .sort([('score', {'$meta': 'textScore'})])

        authors = []
        for author in doc:
            authors.append(Author(author))

        return authors

    def find_one(self, author_id=None, firstname=None, surname=None):
        query = {}
        if author_id is not None: query['_id'] = uuid_from_str(author_id)
        if firstname is not None: query['firstname'] = firstname
        if surname is not None: query['surname'] = surname
            
        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Author(doc)


class Author(object):

    def __init__(self, author):
        self._id = uuid_to_str(author['_id'])
        self._created = author['created']
        self._surname = author['surname']
        self._firstname = author['firstname']

    def serialize(self, update=False):
        author = {
            'firstname': self._firstname,
            'surname': self._surname
        }

        if not update:
            author['_id'] = uuid_from_str(self._id)
            author['created'] = self._created

        return author

    def get_serialized_data(self):
        return {
            'id': self._id,
            'created': self._created.isoformat(),
            'firstname': self._firstname,
            'surname': self._surname
        }

    def get_id(self):
        return self._id

    def get_fullname(self):
        return self._firstname + " " + self._surname


    def set_firstname(self, firstname):
        self._firstname = firstname

    def set_surname(self, surname):
        self._surname = surname

    def __repr__(self):
        return '<%r id=%r name=%r %r>' % (self.__class__.__name__, self._id, self._firstname, self._surname)
