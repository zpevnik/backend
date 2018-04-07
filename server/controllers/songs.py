import math

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
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS
from server.constants import PERMISSION

api = Blueprint('songs', __name__)


@api.route('/songs', methods=['GET', 'POST'])
@login_required
def songs():
    if request.method == 'GET':
        data = validators.handle_GET_request(request.args)

        # find all results for currect user and his unit
        result = g.model.songs.find_filtered(data['query'], data['order'], current_user.get_id())

        # prepare response
        size = len(result)
        response = {
            'data': [],
            'count': size,
            'pages': int(math.ceil(size / data['per_page']))
        } # yapf: disable

        # slice results based on 'page' and 'per_page' values
        result = result[(data['per_page'] * data['page']):(data['per_page'] * (data['page'] + 1))]

        for res in result:
            response['data'].append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.songs_request(data)
        data['owner'] = current_user.get_id()
        data['owner_unit'] = current_user.get_unit()
        data['visibility'] = data['visibility'] if 'visibility' in data else PERMISSION.PRIVATE

        validators.song_format(data)

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
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    if request.method == 'GET':
        if 'Accept' in request.headers and request.headers['Accept'] == 'application/pdf':
            return jsonify(export_song(song)), 200
        return jsonify(song.get_serialized_data()), 200

    elif request.method == 'PUT':
        if not permissions.check_perm(current_user, song, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, 403,
                               (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

        data = request.get_json()
        validators.json_request(data)
        data = validators.songs_request(data)

        for author in data['authors']['music']:
            validators.author_existence(author)
        for author in data['authors']['lyrics']:
            validators.author_existence(author)
        for interpreter in data['interpreters']:
            validators.interpreter_existence(interpreter)

        validators.song_format(data)
        song.set_data(data)

        data['song_id'] = song_id
        g.model.songs.save(song)
        log_event(EVENTS.SONG_EDIT, current_user.get_id(), data)

        return jsonify(song.get_serialized_data()), 200

    else:
        if not permissions.check_perm(current_user, song, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, 403,
                               (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

        g.model.songs.delete(song)
        log_event(EVENTS.SONG_DELETE, current_user.get_id(), song_id)

        return jsonify(), 204


@api.route('/songs/<song_id>/duplicate', methods=['GET'])
@login_required
def song_duplicate(song_id):
    song = validators.song_existence(song_id)
    if not permissions.check_perm(current_user, song, visibility=True):
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    data = song.get_serialized_data()
    data['owner'] = current_user.get_id()
    data['visibility'] = PERMISSION.PRIVATE

    song = g.model.songs.create_song(data)
    log_event(EVENTS.SONG_NEW, current_user.get_id(), data)

    return jsonify(link='songs/{}'.format(song.get_id())), 201, \
          {'location': '/songs/{}'.format(song.get_id())}


app.register_blueprint(api, url_prefix='/api/v1')
