
class Model (object):
    """Main model class, which contains references for all submodels. This class
    initiliaze these submodels.

    Args:
      db: Reference to database

    Attributes:
      songs (server.model.Songs): Submodel for managing songs
    """

    def __init__(self, db):
        from server.model.songs import Songs
        from server.model.authors import Authors
        from server.model.songbooks import Songbooks

        self.songs = Songs(model=self, db=db)
        self.songs = Authors(model=self, db=db)
        self.songs = Songbooks(model=self, db=db)
        