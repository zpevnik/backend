import pystache

from server.constants import OPTIONS
from server.constants import DEFAULTS


class SongTemplate(object):

    def __init__(self, data):
        self._title = data['title']
        self._intepreters = ", ".join(data['interpreters'])
        self._song = data['song']

    def title(self):
        # Song title
        return self._title

    def interpreters(self):
        # Interpreters of given song
        return self._intepreters

    def song(self):
        # Song data itself (translated to LaTeX)
        return self._song


class SongbookTemplate(object):

    def __init__(self, options):
        self.inject_defaults(options)

        if options['format'] == OPTIONS.FORMAT.A4:
            self._format = 'a4paper'
        elif options['format'] == OPTIONS.FORMAT.A5:
            self._format = 'a5paper'
        elif options['format'] == OPTIONS.FORMAT.A4_WIDE:
            self._format = 'a4paper, landscape'
        elif options['format'] == OPTIONS.FORMAT.A5_WIDE:
            self._format = 'a5paper, landscape'

        self._front_index = True if options['index'] and options['front_index'] else False
        self._back_index = True if options['index'] and not options['front_index'] else False

        self._chorded = 'chorded' if options['chorded'] else 'lyric'

        self._columns = options['columns']
        self._page_numbering = options['page_numbering']
        self._song_numbering = options['song_numbering']

    def inject_defaults(self, options):
        # Add missing options to given dict based on songbook defaults.

        if 'format' not in options:
            options['format'] = DEFAULTS.SONGBOOK_OPTIONS['format']
        if 'columns' not in options:
            options['columns'] = DEFAULTS.SONGBOOK_OPTIONS['columns']
        if 'index' not in options:
            options['index'] = DEFAULTS.SONGBOOK_OPTIONS['index']
        if 'chorded' not in options:
            options['chorded'] = DEFAULTS.SONGBOOK_OPTIONS['chorded']
        if 'front_index' not in options:
            options['front_index'] = DEFAULTS.SONGBOOK_OPTIONS['front_index']
        if 'page_numbering' not in options:
            options['page_numbering'] = DEFAULTS.SONGBOOK_OPTIONS['page_numbering']
        if 'song_numbering' not in options:
            options['song_numbering'] = DEFAULTS.SONGBOOK_OPTIONS['song_numbering']

    def set_filename(self, filename):
        self._filename = filename

    def filename(self):
        # Filename of songbook sbd file (without the extension)
        return self._filename

    def format(self):
        # LaTeX documentclass arguments based on format and orientation
        return self._format

    def columns(self):
        # Songs package \songcolumns{} argument
        return self._columns

    def front_index(self):
        # Boolean - whether front index should be rendered
        return self._front_index

    def back_index(self):
        # Boolean - whether back index should be rendered
        return self._back_index

    def chorded(self):
        # Songs package argument for output format
        return self._chorded

    def disable_page_numbering(self):
        # Boolean - whether pages should not have numbers
        return not self._page_numbering

    def disable_song_numbering(self):
        # Boolean - whether songs should not have numbers
        return not self._song_numbering
