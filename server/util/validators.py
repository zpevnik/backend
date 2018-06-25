from flask import g

from server.util.exceptions import AppException
from server.util.translator import translate_to_tex

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import OPTIONS
from server.constants import STRINGS
from server.constants import DEFAULTS
from server.constants import ORDERING
from server.constants import format_dict


def handle_GET_request(request):
    data = {
        'query': request['query'] if 'query' in request and request['query'] is not None else "",
        'page': 0,
        'per_page': 30,
        'order': None
    }

    if 'page' in request and request['page'] is not None:
        if int(request['page']) < 0:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 400,
                               (EXCODES.WRONG_VALUE, STRINGS.REQUEST_PAGE_OOR_ERROR, 'page'))
        data['page'] = int(request['page'])

    if 'per_page' in request and request['per_page'] is not None:
        if int(request['per_page']) < 1 or int(request['per_page']) > 200:
            raise AppException(
                EVENTS.REQUEST_EXCEPTION, 400,
                (EXCODES.WRONG_VALUE, STRINGS.REQUEST_PER_PAGE_OOR_ERROR, 'per_page'))
        data['per_page'] = int(request['per_page'])

    if 'order' in request and request['order'] is not None:
        if request['order'] not in ORDERING:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 400,
                               (EXCODES.WRONG_VALUE, STRINGS.REQUEST_PAGE_OOR_ERROR, 'order'))
        data['order'] = request['order']

    return data


def user_existence(user_id):
    user = g.model.users.find(int(user_id))
    if user is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.USER_NOT_FOUND_ERROR))
    return user


def song_existence(song_id):
    try:
        song = g.model.songs.find_one(song_id=song_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONG_NOT_FOUND_ERROR))

    if song is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONG_NOT_FOUND_ERROR))
    return song


def song_variant_existence(variant_id):
    try:
        variant = g.model.variants.find_one(variant_id=variant_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONG_VARIANT_NOT_FOUND_ERROR))

    if variant is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONG_VARIANT_NOT_FOUND_ERROR))
    return variant


def songbook_existence(songbook_id):
    try:
        songbook = g.model.songbooks.find_one(songbook_id=songbook_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONGBOOK_NOT_FOUND_ERROR))

    if songbook is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.SONGBOOK_NOT_FOUND_ERROR))
    return songbook


def author_existence(author_id):
    try:
        author = g.model.authors.find_one(author_id=author_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.AUTHOR_NOT_FOUND_ERROR))

    if author is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.AUTHOR_NOT_FOUND_ERROR))
    return author


def interpreter_existence(interpreter_id):
    try:
        interpreter = g.model.interpreters.find_one(interpreter_id=interpreter_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.INTERPRETER_NOT_FOUND_ERROR))

    if interpreter is None:
        raise AppException(EVENTS.BASE_EXCEPTION, 404,
                           (EXCODES.DOES_NOT_EXIST, STRINGS.INTERPRETER_NOT_FOUND_ERROR))
    return interpreter


def author_nonexistence(name):
    author = g.model.authors.find_one(name=name)
    if author is not None:
        raise AppException(EVENTS.BASE_EXCEPTION, 422,
                           (EXCODES.ALREADY_EXISTS, STRINGS.AUTHOR_ALREADY_EXISTS_ERROR))
    return True


def interpreter_nonexistence(name):
    interpreter = g.model.interpreters.find_one(name=name)
    if interpreter is not None:
        raise AppException(EVENTS.BASE_EXCEPTION, 422,
                           (EXCODES.ALREADY_EXISTS, STRINGS.INTERPRETER_ALREADY_EXISTS_ERROR))
    return True


def authors_request(request):
    if 'name' not in request or not request['name']:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                           (EXCODES.MISSING_FIELD, STRINGS.REQUEST_AUTHOR_NAME_MISSING, 'name'))
    return {'name': request['name']}


def interpreters_request(request):
    if 'name' not in request or not request['name']:
        raise AppException(
            EVENTS.REQUEST_EXCEPTION, 422,
            (EXCODES.MISSING_FIELD, STRINGS.REQUEST_INTERPRETER_NAME_MISSING, 'name'))
    return {'name': request['name']}


def songs_request(request):
    ex = AppException(EVENTS.REQUEST_EXCEPTION, 422)

    if 'title' not in request or not request['title']:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_TITLE_MISSING, 'title')
    if 'authors' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_AUTHORS_MISSING, 'authors')
    if 'interpreters' not in request:
        ex.add_error(EXCODES.MISSING_FIELD,
            STRINGS.REQUEST_SONG_INTERPRETERS_MISSING, 'interpreters') # yapf: disable

    if ex.errors:
        raise ex

    data = {
        'title': request['title'],
        'authors': request['authors'],
        'interpreters': request['interpreters']
    }

    return data


def songs_extended_request(request):
    ex = AppException(EVENTS.REQUEST_EXCEPTION, 422)

    if 'title' not in request or not request['title']:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_TITLE_MISSING, 'title')
    if 'authors' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_AUTHORS_MISSING, 'authors')
    if 'interpreters' not in request:
        ex.add_error(EXCODES.MISSING_FIELD,
            STRINGS.REQUEST_SONG_INTERPRETERS_MISSING, 'interpreters') # yapf: disable
    if 'variant' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_VARIANT_MISSING, 'variant')
    else:
        if 'text' not in request['variant'] or not request['variant']['text']:
            ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_TEXT_MISSING, 'variant/text')
        if 'description' not in request['variant']:
            ex.add_error(EXCODES.MISSING_FIELD,
                STRINGS.REQUEST_SONG_DESCRIPTION_MISSING, 'variant/description') # yapf: disable

    if ex.errors:
        raise ex

    data = {
        'title': request['title'],
        'authors': request['authors'],
        'interpreters': request['interpreters'],
        'variant': {
            'text': request['variant']['text'],
            'description': request['variant']['description']
        }
    }
    if 'visibility' in request['variant']:
        data['variant']['visibility'] = request['variant']['visibility']

    return data


def song_variant_request(request):
    ex = AppException(EVENTS.REQUEST_EXCEPTION, 422)

    if 'text' not in request or not request['text']:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_TEXT_MISSING, 'text')
    if 'description' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_DESCRIPTION_MISSING, 'description')

    if ex.errors:
        raise ex

    data = {
        'text': request['text'],
        'description': request['description'],
    }
    if 'visibility' in request:
        data['visibility'] = request['visibility']

    return data


def songbooks_request(request):
    ex = AppException(EVENTS.REQUEST_EXCEPTION, 422)

    if 'title' not in request or not request['title']:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_TITLE_MISSING, 'title')
    if 'options' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_OPTIONS_MISSING, 'options')
    if 'songs' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_SONGS_MISSING, 'songs')

    if ex.errors:
        raise ex

    return {'title': request['title'], 'options': request['options'], 'songs': request['songs']}


def songbooks_title_request(request):
    if 'title' not in request or not request['title']:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                           (EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_TITLE_MISSING, 'title'))
    return {'title': request['title']}


def songbooks_songs_request(request):
    if 'songs' not in request:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                           (EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_SONGS_MISSING, 'songs'))
    return {'songs': request['songs']}


def songbooks_options_request(request):
    if 'options' not in request:
        raise AppException(
            EVENTS.REQUEST_EXCEPTION, 422,
            (EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_OPTIONS_MISSING, 'options'))
    return {'options': request['options']}


def songbook_options(data):
    options = {}
    if 'format' in data:
        if data['format'] not in format_dict:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                               (EXCODES.WRONG_VALUE, STRINGS.JSON_REQUEST_ERROR, 'format'))

    options['format'] = data['format'] if 'format' in data else DEFAULTS.SONGBOOK_OPTIONS['format']
    options['columns'] = int(
        data['columns']) if 'columns' in data else DEFAULTS.SONGBOOK_OPTIONS['columns']
    options['index'] = bool(
        data['index']) if 'index' in data else DEFAULTS.SONGBOOK_OPTIONS['index']
    options['chorded'] = bool(
        data['chorded']) if 'chorded' in data else DEFAULTS.SONGBOOK_OPTIONS['chorded']
    options['front_index'] = bool(
        data['front_index']) if 'front_index' in data else DEFAULTS.SONGBOOK_OPTIONS['front_index']
    options['page_numbering'] = bool(
        data['page_numbering']) if 'page_numbering' in data else DEFAULTS.SONGBOOK_OPTIONS['page_numbering'] # yapf: disable
    options['song_numbering'] = bool(
        data['song_numbering']) if 'song_numbering' in data else DEFAULTS.SONGBOOK_OPTIONS['song_numbering'] # yapf: disable

    return options


def songbook_songs(data):

    def _get_position():
        if not songs:
            return 0
        return max((item['order'] if 'order' in item else 0) for item in songs) + 1

    songs = []
    for variant in data:
        if 'variant_id' not in variant:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                               (EXCODES.MISSING_FIELD,
                                STRINGS.REQUEST_SONGBOOK_SONGS_VARIANT_MISSING, 'songs/variant_id'))

        song_variant_existence(variant['variant_id'])
        if 'order' not in variant:
            variant['order'] = _get_position()
        songs.append({'variant_id': variant['variant_id'], 'order': variant['order']})
    return songs


def json_request(request):
    if not request:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 400,
                           (EXCODES.INVALID_REQUEST, STRINGS.JSON_REQUEST_ERROR))
    return True


def song_format(request):
    translation, log = translate_to_tex(request['text'])
    if log:
        raise AppException(EVENTS.COMPILATION_EXCEPTION, 422,
                           (EXCODES.COMPILATION_ERROR, STRINGS.COMPILATION_ERROR, log))
    return translation
