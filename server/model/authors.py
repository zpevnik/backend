from datetime import datetime

from server.util import generate_random_uuid
from server.util import uuid_from_str
from server.util import uuid_to_str


class Authors(object):
    """Collection for managing CRUD operation in database for authors.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'authors'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_author(self, data):
        """Create new author and insert it into database.

        Args:
          data (dict): Author data containing 'firstname'
            and 'surname' dictionary keys.

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
        """Save author into the database.

        Args:
          author (Author): Instance of the author.
        """
        self._collection.update(
            {'_id': uuid_from_str(author.get_id())},
            {'$set': author.serialize(update=True)}
        )

    def delete(self, author):
        """Delete author from the database.

        Args:
          author (Author): Instance of the author.
        """
        self._collection.delete_one(
            {'_id': uuid_from_str(author.get_id())}
        )

    def find_special(self, query, page, per_page):
        """Find authors from the database based on query and page the result.

        Args:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of authors per search result.

        If the query string is empty, whole database is returned (and paged).

        Returns:
          list: List of Author instances satisfying the query.
        """
        if query is None or query == "":
            doc = self._collection.find({}).skip(page * per_page) \
                                  .limit(per_page)
        else:
            doc = self._collection.find({'$text':{'$search': query}},
                                        {'score': {'$meta': "textScore"}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) \
                                  .skip(page * per_page).limit(per_page)

        authors = []
        for author in doc:
            authors.append(Author(author))

        return authors

    def find_one(self, author_id=None, firstname=None, surname=None):
        """Find one author based on given arguments.

        Args:
          author_id (str, optional): Author UUID.
          firstname (str, optional): First name of the author.
          surname (str, optional): Surname of the author.

        Returns:
          Author: One Author or None if it does not exist.
        """
        query = {}
        if author_id is not None:
            query['_id'] = uuid_from_str(author_id)
        if firstname is not None:
            query['firstname'] = firstname
        if surname is not None:
            query['surname'] = surname

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Author(doc)


class Author(object):
    """Class for author abstraction.

    Args:
      author (dict): Author dictionary.

    Attributes:
      _id (str): Author UUID.
      _created (str): Timestamp of the author creation.
      _firstname (str): Author first name.
      _surname (str): Author surname.
    """

    def __init__(self, author):
        self._id = uuid_to_str(author['_id'])
        self._created = author['created']
        self._surname = author['surname']
        self._firstname = author['firstname']

    def serialize(self, update=False):
        """Serialize author data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """
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
        return "{!s} {!s}".format(self._firstname, self._surname)

    def set_firstname(self, firstname):
        self._firstname = firstname

    def set_surname(self, surname):
        self._surname = surname

    def __repr__(self):
        return '<{!r} id={!r} name={!r}>' \
            .format(self.__class__.__name__, self._id, self.get_fullname())
