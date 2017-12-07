from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import export_songbook
from server.util import permissions
from server.util import validators
from server.util import log_event
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import STRINGS
from server.constants import PERMISSION

api = Blueprint('songbooks', __name__)


@api.route('/songbooks', methods=['GET', 'POST'])
@login_required
def songbooks():
    if request.method == 'GET':
        data = validators.handle_GET_request(request.args)

        # find all results for currect user
        result = g.model.songbooks.find_filtered(data['query'], current_user.get_id())

        # slice results based on 'page' and 'per_page' values
        result = result[(data['per_page'] * data['page']):(data['per_page'] * (data['page'] + 1))]

        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.songbooks_request(data)
        data['owner'] = current_user.get_id()
        data['owner_unit'] = current_user.get_unit()
        data['visibility'] = PERMISSION.PRIVATE
        data['edit_perm'] = PERMISSION.PRIVATE

        songbook = g.model.songbooks.create_songbook(data)
        log_event(EVENTS.SONGBOOK_NEW, current_user.get_id(), data)

        return jsonify(link='songbooks/{}'.format(songbook.get_id())), 201, \
              {'location': '/songbooks/{}'.format(songbook.get_id())}


@api.route('/songbooks/<songbook_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def songbook_single(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if not permissions.check_perm(current_user, songbook, visibility=True):
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    if request.method == 'GET':
        if request.headers['Accept'] == 'application/pdf':
            return jsonify(export_songbook(songbook)), 200
        return jsonify(songbook.get_serialized_data()), 200

    elif request.method == 'PUT':
        if not permissions.check_perm(current_user, songbook, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        data = request.get_json()
        validators.json_request(data)
        data = validators.songbooks_request(data)

        songbook.set_data(data)
        g.model.songbooks.save(songbook)

        data['songbook_id'] = songbook_id
        log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

        return jsonify(songbook.get_serialized_data()), 200

    else:
        if not permissions.check_perm(current_user, songbook, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        g.model.songbooks.delete(songbook)
        log_event(EVENTS.SONGBOOK_DELETE, current_user.get_id(), songbook_id)

        return jsonify(), 204


@api.route('/songbooks/<songbook_id>/song/<song_id>', methods=['PUT', 'DELETE'])
@login_required
def songbook_song_single(songbook_id, song_id):
    songbook = validators.songbook_existence(songbook_id)
    if not permissions.check_perm(current_user, songbook, visibility=True, editing=True):
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    if request.method == 'PUT':
        song = validators.song_existence(song_id)

        data = request.get_json()
        validators.json_request(data)
        data = validators.songbooks_song_request(data)

        if not permissions.check_perm(current_user, song, visibility=True):
            raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        songbook.set_song(song_id, data)
        g.model.songbooks.save(songbook)

        data['id'] = song_id
        log_event(EVENTS.SONGBOOK_SET_SONG, current_user.get_id(), {
            'songbook': songbook_id,
            'song': song_id
        })

        return jsonify({'message': STRINGS.SONGBOOK_SET_SONG_SUCCESS}), 200

    else:
        songbook.remove_song(song_id)
        g.model.songbooks.save(songbook)
        log_event(EVENTS.SONGBOOK_REMOVE_SONG, current_user.get_id(), song_id)

        return jsonify(), 204


@api.route('/songbooks/<songbook_id>/songs', methods=['PUT'])
@login_required
def songbook_song_bulk(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if not permissions.check_perm(current_user, songbook, visibility=True, editing=True):
        raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    data = request.get_json()
    validators.json_request(data)

    for entry in data:
        entry = validators.songbooks_song_request(entry)
        song = validators.song_existence(entry['id'])
        if not permissions.check_perm(current_user, song, visibility=True):
            raise AppException(EVENTS.BASE_EXCEPTION, STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        songbook.set_song(entry['id'], entry)

        log_event(EVENTS.SONGBOOK_SET_SONG, current_user.get_id(), {
            'songbook': songbook_id,
            'song': entry['id']
        })

    g.model.songbooks.save(songbook)
    return jsonify({'message': STRINGS.SONGBOOK_SET_SONG_SUCCESS}), 200


app.register_blueprint(api, url_prefix='/api/v1')
