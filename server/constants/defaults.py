from server.constants import OPTIONS


class Defaults(object):
    SONGBOOK_OPTIONS = {
        'size': OPTIONS.SIZE.A4,
        'columns': 2,
        'index': True,
        'chorded': True,
        'front_index': False,
        'page_numbering': True
    }


DEFAULTS = Defaults()
