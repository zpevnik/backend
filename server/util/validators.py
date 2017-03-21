from flask import g
from server.util.exceptions import AppException


def request_GET(request):
    if 'page' in request and request['page'] is not None:
        if request['page'] < 0:
            raise AppException('error', 'page_out_of_range', 'Page number is out of range.', status_code=400)

    if 'per_page' in request and request['per_page'] is not None:
        if request['per_page'] < 1 or request['per_page'] > 100:
            raise AppException('error', 'per_page_out_of_range', 'Per page number is out of range.', status_code=400)
    return True


def author_existence(author_id):
    author = g.model.authors.find_one(author_id=author_id)
    if author is None:
        raise AppException('error', 'author_does_not_exist', 'Autor nebyl nalezen', status_code=404)
    return author

def author_nonexistence(firstname, surname):
    author = g.model.authors.find_one(firstname=firstname, surname=surname)
    if author is not None:
        raise AppException('error', 'author_exist', 'Author already exist.', status_code=400)
    return author

def song_existence(song_id):
    song = g.model.songs.find_one(song_id=song_id)
    if song is None:
        raise AppException('error', 'song_does_not_exist', 'Song with id `%s` doesn\'t exist.' % song_id)
    return song

def songbook_existence(songbook_id):
    songbook = g.model.songbooks.find_one(songbook_id=songbook_id)
    if songbook is None:
        raise AppException('error', 'songbook_does_not_exist', 'Songbook with id `%s` doesn\'t exist.' % songbook_id)
    return songbook


def authors_POST(request):
    if 'firstname' not in request or not request['firstname']:
        raise AppException('error', 'authors_firstname_missing', 'Author name is missing', status_code=422)
    if 'surname' not in request or not request['surname']:
        raise AppException('error', 'authors_surname_missing', 'Author surname is missing.', status_code=422)
    return True

def songs_POST(request):
    if 'title' not in request or not request['title']:
        raise AppException('error', 'song_title_missing', 'Song title is missing', status_code=422)
    return True

def variants_POST(request):
    if 'title' not in request or not request['title']:
        raise AppException('error', 'variant_title_missing', 'Variant title is missing', status_code=422)
    if 'text' not in request or not request['text']:
        raise AppException('error', 'variant_text_missing', 'Variant text is missing', status_code=422)
    return True

def songbooks_POST(request):
    if 'title' not in request or not request['title']:
        raise AppException('error', 'songbook_title_missing', 'Songbook title is missing', status_code=422)
    return True
