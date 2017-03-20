from flask import g
from datetime import datetime

from server.util import generate_random_uuid, uuid_from_str, uuid_to_str
from server.util.exceptions import AppException

import logging
logger = logging.getLogger(__name__)

class Variants(object):
    """Collection for managing CRUD operation in database for variants

    Args:
      model (server.model.Model): Reference to model
      db (pymongo.MongoClient): Reference to database

    Attributes:
      _model (server.model.Model): Reference to model
      _db: Reference to database
      _collection: Reference to collection in database for this class
    """

    COLLECTION_NAME = 'variants'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_variant(self, data):
        """Create new variant instance and insert it into database.

        Args:
          data (dict): Data about the variant (title, authors and text).

        Returns:
          Variant: Instance of the new variant.
        """
        variant = Variant({
            '_id': generate_random_uuid(),
            'created': datetime.utcnow(),
            'title': data['title'],
            'text': data['text'],
            'authors': data['authors'] if 'authors' in data else ''
        })
        self._collection.insert(variant.serialize())

        return variant

    def save(self, variant):
        """Save instance of variant into database.

        Args:
          variant (Variant): instance of the variant.
        """
        self._collection.update(
            {'_id': uuid_from_str(variant.get_id())},
            {'$set': variant.serialize(update=True)}
        )

    def delete(self, variant):
        """Delete variant from the database.

        Args:
          variant (Variant): instance of the variant.
        """
        self._collection.delete_one(
            {'_id': uuid_from_str(variant.get_id())}
        )

    def find(self):
        """Find all the variants satisfying given restrictions 
        (currently no restrictions).

        Returns:
          list: List of variant instances or None.
        """
        doc = self._collection.find({})

        if doc.count() == 0:
            return []

        variants = []
        for variant in doc:
            variants.append(Variant(variant))

        return variants


class Variant(object):
    """Class for variant abstraction.

    Args:
      variant (dict): Island dictionary.

    Attributes:
      _id (str): Island UUID.
      _created (str): Timestamp of the island creation.
      _authors (str): Authors...
      _title (str): Title of the variant.
      _text (str): Lyrics and chords of the variant.
    """

    def __init__(self, variant):
        self._id = uuid_to_str(variant['_id'])
        self._created = variant['created']
        self._authors = variant['authors']
        self._title = variant['title']
        self._text = variant['text']

    def serialize(self, update=False):
        variant = {
            'authors': self._authors,
            'title': self._title,
            'text': self._text
        }

        if not update:
            variant['_id'] = uuid_from_str(self._id)
            variant['created'] = self._created

        return variant

    def get_id(self):
        return self._id

    def generate_tex(self, filename):
        with open('variants/sample/sample.sbd', 'r') as file:
            filedata = file.read()

        # todo translate variant
        with open('test.variant', 'r') as file:
            variant = file.read()

        filedata = filedata.replace('$title$', self._title)
        filedata = filedata.replace('$authors$', self._authors )
        filedata = filedata.replace('$variant$', variant)

        with open('variants/temp/' + filename + '.sbd', 'a') as file:
            file.write(filedata)


    def __repr__(self):
        return '<%r id=%r title=%r authors=%r>' % (self.__class__.__name__, self._id, self._title, self._authors)
