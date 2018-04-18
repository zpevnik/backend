from server.constants import OPTIONS


class Defaults(object):
    SONGBOOK_OPTIONS = {
        'format': OPTIONS.FORMAT.A4,
        'columns': 2,
        'index': True,
        'chorded': True,
        'front_index': False,
        'page_numbering': True,
        'song_numbering': False
    }


DEFAULTS = Defaults()
