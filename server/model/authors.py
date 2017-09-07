from bson import ObjectId


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
          data (dict): Author data containing 'name' dictionary keys.

        Returns:
          Author: Instance of the new author.
        """
        author = Author({
            '_id': ObjectId(),
            'name': data['name']
        })
        self._collection.insert(author.serialize())
        return author

    def save(self, author):
        """Save author into the database.

        Args:
          author (Author): Instance of the author.
        """
        self._collection.update(
            {'_id': author._id},
            {'$set': author.serialize(update=True)}
        )

    def delete(self, author):
        """Delete author from the database.

        Args:
          author (Author): Instance of the author.
        """
        self._collection.delete_one({'_id': author._id})

    def find(self):
        """Find all authors in the database."""
        doc = self._collection.find({})

        authors = []
        for author in doc:
            authors.append(Author(author))

        return authors

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

    def find_one(self, author_id=None, name=None):
        """Find one author based on given arguments.

        Args:
          author_id (str, optional): Author ObjectId string.
          name (str, optional): Name of the author.

        Returns:
          Author: One Author or None if it does not exist.
        """
        query = {}
        if author_id is not None:
            query['_id'] = ObjectId(author_id)
        if name is not None:
            query['name'] = name

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Author(doc)


class Author(object):
    """Class for author abstraction.

    Args:
      author (dict): Author dictionary.

    Attributes:
      _id (str): Author ObjectId.
      _name (str): Author name.
    """

    def __init__(self, author):
        self._id = author['_id']
        self._name = author['name']

    def serialize(self, update=False):
        """Serialize author data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """
        author = {'name': self._name}

        if not update:
            author['_id'] = self._id

        return author

    def get_serialized_data(self):
        return {
            'id': str(self._id),
            'created': self._id.generation_time,
            'name': self._name,
        }

    def get_id(self):
        return str(self._id)

    def get_creation_date(self):
        return self._id.generation_time

    def get_name(self):
        return self._name

    def set_data(self, data):
        self._name = data['name'] if 'name' in data else self._name

    def __repr__(self):
        return '<{!r} id={!r} name={!r}>' \
            .format(self.__class__.__name__, self._id, self._name)
