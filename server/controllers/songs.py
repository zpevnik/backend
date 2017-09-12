from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import export_song
from server.util import permissions
from server.util import validators
from server.util import log_event
from server.util.exceptions import ClientException

from server.constants import EVENTS
from server.constants import STRINGS
from server.constants import PERMISSION

api = Blueprint('songs', __name__)


@api.route('/songs', methods=['GET', 'POST'])
@login_required
def songs():
    if request.method == 'GET':
        data = validators.handle_GET_request(request.args)
        data['user'] = current_user.get_id()
        data['unit'] = current_user.get_unit()

        result = g.model.songs.find_special(data)
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.songs_request(data)
        data['owner'] = current_user.get_id()
        data['owner_unit'] = current_user.get_unit()
        data['visibility'] = PERMISSION.PRIVATE
        data['edit_perm'] = PERMISSION.PRIVATE

        for author in data['authors']['music']:
            validators.author_existence(author)
        for author in data['authors']['lyrics']:
            validators.author_existence(author)
        for interpreter in data['interpreters']:
            validators.interpreter_existence(interpreter)

        song = g.model.songs.create_song(data)
        log_event(EVENTS.SONG_NEW, current_user.get_id(), data)

        return jsonify(link='songs/{}'.format(song.get_id())), 201, \
              {'location': '/songs/{}'.format(song.get_id())}


@api.route('/songs/<song_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def song_single(song_id):
    song = validators.song_existence(song_id)
    if not permissions.check_perm(current_user, song, visibility=True):
        raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    if request.method == 'GET':
        if request.headers['Content-Type'] == 'application/pdf':
            return jsonify(export_song(song)), 200
        return jsonify(song.get_serialized_data()), 200

    elif request.method == 'PUT':
        if not permissions.check_perm(current_user, song, editing=True):
            raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        data = request.get_json()
        validators.json_request(data)
        data = validators.songs_request(data)

        for author in data['authors']['music']:
            validators.author_existence(author)
        for author in data['authors']['lyrics']:
            validators.author_existence(author)
        for interpreter in data['interpreters']:
            validators.interpreter_existence(interpreter)

        song.set_data(data)

        data['song_id'] = song_id
        g.model.songs.save(song)
        log_event(EVENTS.SONG_EDIT, current_user.get_id(), data)

        return jsonify(song.get_serialized_data()), 200

    else:
        if not permissions.check_perm(current_user, song, editing=True):
            raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

        g.model.songs.delete(song)
        log_event(EVENTS.SONG_DELETE, current_user.get_id(), song_id)

        return jsonify(), 204


app.register_blueprint(api, url_prefix='/api/v1')
