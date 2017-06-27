from flask import g
from server.util.exceptions import ClientException
from server.util.exceptions import ValidationException
from server.util.exceptions import RequestException

def request_GET(request):
    if 'page' in request and request['page'] is not None:
        if request['page'] < 0:
            raise ClientException('Page number is out of range.', 400)

    if 'per_page' in request and request['per_page'] is not None:
        if request['per_page'] < 1 or request['per_page'] > 10000:
            raise ClientException('Per page number is out of range.', 400)
    return True


def author_existence(author_id):
    try:
        author = g.model.authors.find_one(author_id=author_id)
    except ValueError:
        raise ClientException('Autor nebyl nalezen.', 404)

    if author is None:
        raise ClientException('Autor nebyl nalezen.', 404)
    return author

def author_nonexistence(firstname, surname):
    author = g.model.authors.find_one(firstname=firstname, surname=surname)
    if author is not None:
        raise ValidationException('Author already exist.', 422, 
                                  errors=[{'field': None,
                                           'code': 'already_exists',
                                           'message': 'Autor již existuje.'}])
    return author

def song_existence(song_id):
    try:
        song = g.model.songs.find_one(song_id=song_id)
    except ValueError:
        raise ClientException('Given song id is not valid.', 404)

    if song is None:
        raise ClientException('Píseň nebyla nalezena.', 404)
    return song

def songbook_existence(songbook_id):
    try:
        songbook = g.model.songbooks.find_one(songbook_id=songbook_id)
    except ValueError:
        raise ClientException('Given song id is not valid.', 404)

    if songbook is None:
        raise ClientException('Zpěvník nebyl nalezen.', 404)
    return songbook


def authors_request(request):
    err = []
    if 'firstname' not in request or not request['firstname']:
        err.append({'field': 'firstname',
                    'code': 'missing_field',
                    'message': 'Author first name is missing'})
    #if 'surname' not in request or not request['surname']:
    #    err.append({'field': 'surname',
    #                'code': 'missing_field',
    #                'message': 'Author surname name is missing'})
    if err:
        raise ValidationException('Cannot process variants POST request.', 422, errors=err)
    return True

def songs_request(request):
    if 'title' not in request or not request['title']:
        err = [{'field': 'title',
                'code': 'missing_field',
                'message': 'Song title is missing'}]
        raise ValidationException('Cannot process songs POST request.', 422, errors=err)
    return True

def variants_request(request):
    err = []
    if 'title' not in request or not request['title']:
        err.append({'field': 'title',
                    'code': 'missing_field',
                    'message': 'Song title is missing'})
    if 'text' not in request or not request['text']:
        err.append({'field': 'text',
                    'code': 'missing_field',
                    'message': 'Song text is missing'})
    if err:
        raise ValidationException('Cannot process variants POST request.', 422, errors=err)
    return True

def songbooks_request(request):
    if 'title' not in request or not request['title']:
        err = [{'field': 'title',
                'code': 'missing_field',
                'message': 'Songbook title is missing'}]
        raise ValidationException('Cannot process songs POST request.', 422, errors=err)
    return True

def json_request(request):
    if not request:
        raise RequestException('Cannot process json request.', 400)
    return True
