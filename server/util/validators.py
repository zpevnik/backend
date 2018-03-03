from flask import g

from server.util.exceptions import AppException
from server.util.translator import translate_to_tex

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import OPTIONS
from server.constants import STRINGS
from server.constants import ORDERING
from server.constants import size_dict


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
    if 'text' not in request or not request['text']:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_TEXT_MISSING, 'text')
    if 'description' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_DESCRIPTION_MISSING, 'description')
    if 'authors' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_AUTHORS_MISSING, 'authors')
    if 'interpreters' not in request:
        ex.add_error(EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONG_INTERPRETERS_MISSING,
                     'interpreters')

    if ex.errors:
        raise ex

    data = {
        'title': request['title'],
        'text': request['text'],
        'authors': request['authors'],
        'description': request['description'],
        'interpreters': request['interpreters']
    }
    if 'visibility' in request:
        data['visibility'] = request['visibility']
    if 'edit_perm' in request:
        data['edit_perm'] = request['edit_perm']

    return data


def songbooks_request(request):
    if 'title' not in request or not request['title']:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                           (EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_TITLE_MISSING, 'title'))

    data = {
        'title': request['title'],
        'options': request['options'] if 'options' in request else {},
        'songs': request['songs'] if 'songs' in request else []
    }

    return data


def songbook_songs_request(request):
    data = {'set': [], 'delete': []}
    if 'set' in request:
        if not isinstance(request['set'], list):
            raise AppException(
                EVENTS.REQUEST_EXCEPTION, 422,
                (EXCODES.WRONG_VALUE, STRINGS.REQUEST_SONGBOOK_SONGS_INVALID, 'delete'))

        for entry in request['set']:
            if 'id' not in entry or not entry['id']:
                raise AppException(
                    EVENTS.REQUEST_EXCEPTION, 422,
                    (EXCODES.MISSING_FIELD, STRINGS.REQUEST_SONGBOOK_ADD_SONG_MISSING, 'id'))

            obj = {'id': entry['id']}
            if 'order' in entry:
                obj['order'] = entry['order']

            data['set'].append(obj)

    if 'delete' in request:
        if not isinstance(request['delete'], list):
            raise AppException(
                EVENTS.REQUEST_EXCEPTION, 422,
                (EXCODES.WRONG_VALUE, STRINGS.REQUEST_SONGBOOK_SONGS_INVALID, 'delete'))

        data['delete'] = request['delete']

    return data


def songbook_options(data):
    options = {}
    if 'size' in data:
        if data['size'] not in size_dict:
            raise AppException(EVENTS.REQUEST_EXCEPTION, 422,
                               (EXCODES.WRONG_VALUE, STRINGS.JSON_REQUEST_ERROR, 'size'))

        options['size'] = data['size']
    if 'columns' in data:
        options['columns'] = int(data['columns'])
    if 'index' in data:
        options['index'] = bool(data['index'])
    if 'chorded' in data:
        options['chorded'] = bool(data['chorded'])
    if 'front_index' in data:
        options['front_index'] = bool(data['front_index'])
    if 'page_numbering' in data:
        options['page_numbering'] = bool(data['page_numbering'])

    return options


def songbook_songs(data):

    def _get_position(self):
        if not songs:
            return 0
        return max((item['order'] if 'order' in item else 0) for item in songs) + 1

    songs = []
    for song in data:
        validators.song_existence(song['id'])
        if 'order' not in song:
            song['order'] = _get_position()
        songs.append({'id': song['id'],'order': song['order']})
    return songs


def json_request(request):
    if not request:
        raise AppException(EVENTS.REQUEST_EXCEPTION, 400,
                           (EXCODES.INVALID_REQUEST, STRINGS.JSON_REQUEST_ERROR))
    return True


def song_format(request):
    _, log = translate_to_tex(request['text'])
    if log:
        raise AppException(EVENTS.COMPILATION_EXCEPTION, 422,
                           (EXCODES.COMPILATION_ERROR, STRINGS.COMPILATION_ERROR, log))
    return True
