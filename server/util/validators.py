from flask import g

from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import OPTIONS
from server.constants import STRINGS
from server.constants import size_dict


def handle_GET_request(request):
    data = {
        'query': request['query'] if 'query' in request and request['query'] is not None else "",
        'page': 0,
        'per_page': 30
    }

    if 'page' in request and request['page'] is not None:
        if int(request['page']) < 0:
            raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.REQUEST_PAGE_OOR_ERROR, 400)
        data['page'] = int(request['page'])

    if 'per_page' in request and request['per_page'] is not None:
        if int(request['per_page']) < 1 or int(request['per_page']) > 200:
            raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.REQUEST_PER_PAGE_OOR_ERROR, 400)
        data['per_page'] = int(request['per_page'])

    return data


def user_existence(user_id):
    user = g.model.users.find(int(user_id))
    if user is None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.USER_NOT_FOUND_ERROR, 422)
    return user


def song_existence(song_id):
    try:
        song = g.model.songs.find_one(song_id=song_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.SONG_NOT_FOUND_ERROR, 422)

    if song is None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.SONG_NOT_FOUND_ERROR, 422)
    return song


def songbook_existence(songbook_id):
    try:
        songbook = g.model.songbooks.find_one(songbook_id=songbook_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.SONGBOOK_NOT_FOUND_ERROR, 422)

    if songbook is None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.SONGBOOK_NOT_FOUND_ERROR, 422)
    return songbook


def author_existence(author_id):
    try:
        author = g.model.authors.find_one(author_id=author_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.AUTHOR_NOT_FOUND_ERROR, 422)

    if author is None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.AUTHOR_NOT_FOUND_ERROR, 422)
    return author


def interpreter_existence(interpreter_id):
    try:
        interpreter = g.model.interpreters.find_one(interpreter_id=interpreter_id)
    except ValueError:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.INTERPRETER_NOT_FOUND_ERROR, 422)

    if interpreter is None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.INTERPRETER_NOT_FOUND_ERROR, 422)
    return interpreter


def author_nonexistence(name):
    author = g.model.authors.find_one(name=name)
    if author is not None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.AUTHOR_ALREADY_EXISTS_ERROR, 422)
        #raise AppException(
        #    EVENTS.BASE_EXCEPTION,
        #    STRINGS.AUTHOR_ALREADY_EXISTS_ERROR,
        #    422,
        #    errors=[{
        #        'field': None,
        #        'code': 'already_exists',
        #        'message': STRINGS.AUTHOR_ALREADY_EXISTS_ERROR
        #    }])
    return True


def interpreter_nonexistence(name):
    interpreter = g.model.interpreters.find_one(name=name)
    if interpreter is not None:
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.INTERPRETER_ALREADY_EXISTS_ERROR, 422)
        #raise AppException(
        #    EVENTS.BASE_EXCEPTION,
        #    STRINGS.INTERPRETER_ALREADY_EXISTS_ERROR,
        #    422,
        #    errors=[{
        #        'field': None,
        #        'code': 'already_exists',
        #        'message': STRINGS.INTERPRETER_ALREADY_EXISTS_ERROR
        #    }])
    return True


def authors_request(request):
    if 'name' not in request or not request['name']:
        err = [{
            'field': 'name',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_AUTHOR_NAME_MISSING
        }]
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.POST_REQUEST_ERROR, 422, data=err)
    return {'name': request['name']}


def interpreters_request(request):
    if 'name' not in request or not request['name']:
        err = [{
            'field': 'name',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_INTERPRETER_NAME_MISSING
        }]
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.POST_REQUEST_ERROR, 422, data=err)
    return {'name': request['name']}


def songs_request(request):
    err = []
    if 'title' not in request or not request['title']:
        err.append({
            'field': 'title',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONG_TITLE_MISSING
        })
    if 'text' not in request or not request['text']:
        err.append({
            'field': 'text',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONG_TEXT_MISSING
        })
    if 'description' not in request:
        err = [{
            'field': 'description',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONG_DESCRIPTION_MISSING
        }]
    if 'authors' not in request:
        err = [{
            'field': 'authors',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONG_AUTHORS_MISSING
        }]
    if 'interpreters' not in request:
        err = [{
            'field': 'interpreters',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONG_INTERPRETERS_MISSING
        }]

    if err:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.POST_REQUEST_ERROR, 422, data=err)

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
        err = [{
            'field': 'title',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONGBOOK_TITLE_MISSING
        }]
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.POST_REQUEST_ERROR, 422, data=err)

    data = {'title': request['title']}
    if 'visibility' in request:
        data['visibility'] = request['visibility']
    if 'edit_perm' in request:
        data['edit_perm'] = request['edit_perm']

    return data


def songbooks_song_request(request):
    if 'id' not in request or not request['id']:
        err = [{
            'field': 'id',
            'code': 'missing_field'
            #'message': STRINGS.REQUEST_SONGBOOK_ADD_SONG_MISSING
        }]
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.POST_REQUEST_ERROR, 422, data=err)

    data = {'id': request['id']}
    if 'order' in request:
        data['order'] = request['order']
    if 'options' in request:
        data['options'] = request['options']

    return data


def songbook_options(data):
    options = {}
    if 'size' in data:
        if data['size'] not in size_dict:
            raise AppException(
                EVENTS.REQUEST_EXCEPTION,
                STRINGS.SONGBOOK_OPTIONS_ERROR,
                422,
                data=[{
                    'field': 'size',
                    'code': 'wrong_value',
                    #'message': STRINGS.SONGBOOK_OPTIONS_SIZE_ERROR
                }])
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


def json_request(request):
    if not request:
        raise AppException(EVENTS.REQUEST_EXCEPTION, STRINGS.JSON_REQUEST_ERROR, 400)
    return True
