from bson import ObjectId


class Interpreters(object):
    """Collection for managing CRUD operation in database for interpreters.

    Args:
      model (server.model.Model): Reference to model.
      db (pymongo.MongoClient): Reference to database.

    Attributes:
      _model (server.model.Model): Reference to model.
      _db: Reference to database.
      _collection: Reference to collection in database for this class.
    """

    COLLECTION_NAME = 'interpreters'

    def __init__(self, model, db):
        self._model = model
        self._db = db
        self._collection = db[self.COLLECTION_NAME]

    def create_interpreter(self, data):
        """Create new interpreter and insert it into database.

        Args:
          data (dict): Interpreter data containing 'name' dictionary keys.

        Returns:
          Interpreter: Instance of the new interpreter.
        """
        interpreter = Interpreter({
            '_id': ObjectId(),
            'name': data['name']
        })
        self._collection.insert_one(interpreter.serialize())
        return interpreter

    def save(self, interpreter):
        """Save interpreter into the database.

        Args:
          interpreter (Interpreter): Instance of the interpreter.
        """
        self._collection.update_one(
            {'_id': interpreter._id},
            {'$set': interpreter.serialize(update=True)}
        )

    def delete(self, interpreter):
        """Delete interpreter from the database.

        Args:
          interpreter (Interpreter): Instance of the interpreter.
        """
        self._collection.delete_one({'_id': interpreter._id})

    def find(self):
        """Find all interpreters in the database."""
        doc = self._collection.find({})

        interpreters = []
        for interpreter in doc:
            interpreters.append(Interpreter(interpreter))

        return interpreters

    def find_special(self, query, page, per_page):
        """Find interpreters from the database based on query and page the result.

        Args:
          query (str): Query string.
          page (int): Result page number.
          per_page (int): Number of interpreters per search result.

        If the query string is empty, whole database is returned (and paged).

        Returns:
          list: List of Interpreter instances satisfying the query.
        """
        if query is None or query == "":
            doc = self._collection.find({}).skip(page * per_page) \
                                  .limit(per_page)
        else:
            doc = self._collection.find({'$text':{'$search': query}},
                                        {'score': {'$meta': "textScore"}}) \
                                  .sort([('score', {'$meta': 'textScore'})]) \
                                  .skip(page * per_page).limit(per_page)

        interpreters = []
        for interpreter in doc:
            interpreters.append(Interpreter(interpreter))

        return interpreters

    def find_one(self, interpreter_id=None, name=None):
        """Find one interpreter based on given arguments.

        Args:
          interpreter_id (str, optional): Interpreter ObjectId string.
          name (str, optional): Name of the interpreter.

        Returns:
          Interpreter: One Interpreter or None if it does not exist.
        """
        query = {}
        if interpreter_id is not None:
            query['_id'] = ObjectId(interpreter_id)
        if name is not None:
            query['name'] = name

        doc = self._collection.find_one(query)
        if not doc:
            return None

        return Interpreter(doc)


class Interpreter(object):
    """Class for interpreter abstraction.

    Args:
      interpreter (dict): Interpreter dictionary.

    Attributes:
      _id (str): Interpreter ObjectId.
      _name (str): Interpreter name.
    """

    def __init__(self, interpreter):
        self._id = interpreter['_id']
        self._name = interpreter['name']

    def serialize(self, update=False):
        """Serialize interpreter data for database operations.

        Args:
          update (bool, optional): Determines whether method returns only
            update attributes or data for new database entry.
        """
        interpreter = {'name': self._name}

        if not update:
            interpreter['_id'] = self._id

        return interpreter

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
