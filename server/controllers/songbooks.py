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
from server.util.exceptions import ClientException

from server.constants import EVENTS
from server.constants import STRINGS
from server.constants import PERMISSION

api = Blueprint('songbooks', __name__)


@api.route('/songbooks', methods=['GET', 'POST'])
@login_required
def songbooks():
    if request.method == 'GET':
        data = validators.handle_GET_request(request.args)
        data['user'] = current_user.get_id()
        data['unit'] = current_user.get_unit()

        result = g.model.songbooks.find_special(data)
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
        raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    if request.method == 'GET':
        if request.headers['Content-Type'] == 'application/pdf':
            return export_songbook(songbook), 200
        return jsonify(songbook.get_serialized_data()), 200

    elif request.method == 'PUT':
        if not permissions.check_perm(current_user, songbook, editing=True):
            raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        data = request.get_json()
        validators.json_request(data)
        data = validators.songbooks_request(data)

        songbook.set_data(data)

        data['songbook_id'] = songbook_id
        g.model.songbooks.save(songbook)
        log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

        return jsonify(songbook.get_serialized_data()), 200

    else:
        if not permissions.check_perm(current_user, songbook, editing=True):
            raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        g.model.songbooks.delete(songbook)
        log_event(EVENTS.SONGBOOK_DELETE, current_user.get_id(), songbook_id)

        return jsonify(), 204


@api.route('/songbooks/<songbook_id>/song/<song_id>', methods=['POST', 'DELETE'])
@login_required
def songbook_song_variants(songbook_id, song_id):
    songbook = validators.songbook_existence(songbook_id)
    if not permissions.check_perm(current_user, songbook, visibility=True, editing=True):
        raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    if request.method == 'POST':
        song = validators.song_existence(song_id)
        if not permissions.check_perm(current_user, song, visibility=True):
            raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        songbook.add_song(song_id, None)
        g.model.songbooks.save(songbook)
        log_event(EVENTS.SONGBOOK_ADD_SONG,
                  current_user.get_id(), {'songbook': songbook_id,
                                          'song': song_id})

        return jsonify({'message': STRINGS.SONGBOOK_ADD_SONG_SUCCESS}), 200

    else:
        songbook.remove_song(song_id)
        g.model.songbooks.save(songbook)
        log_event(EVENTS.SONGBOOK_REMOVE_SONG, current_user.get_id(), song_id)

        return jsonify(), 204


app.register_blueprint(api, url_prefix='/api/v1')
