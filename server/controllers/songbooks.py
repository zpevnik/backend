import math

from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
from server.util import export_songbook
from server.util import validators
from server.util import log_event
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import EXCODES
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

        data = validators.songbooks_title_request(data)
        data['owner'] = current_user.get_id()
        data['owner_unit'] = current_user.get_unit()

        songbook = g.model.songbooks.create_songbook(data)
        log_event(EVENTS.SONGBOOK_NEW, current_user.get_id(), data)

        return jsonify(link='songbooks/{}'.format(songbook.get_id())), 201, \
              {'location': '/songbooks/{}'.format(songbook.get_id())}


@api.route('/songbooks/<songbook_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def songbook_single(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if current_user.get_id() != songbook.get_owner():
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    if request.method == 'GET':
        if 'Accept' in request.headers and request.headers['Accept'] == 'application/pdf':
            return jsonify(export_songbook(songbook)), 200
        return jsonify(songbook.get_serialized_data()), 200

    elif request.method == 'PUT':
        data = request.get_json()
        validators.json_request(data)
        data = validators.songbooks_request(data)

        data['options'] = validators.songbook_options(data['options'])
        data['songs'] = validators.songbook_songs(data['songs'])

        songbook.set_data(data)
        g.model.songbooks.save(songbook)

        data['songbook_id'] = songbook_id
        log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

        return jsonify(songbook.get_serialized_data()), 200

    else:
        g.model.songbooks.delete(songbook)
        log_event(EVENTS.SONGBOOK_DELETE, current_user.get_id(), songbook_id)

        return jsonify(), 204


@api.route('/songbooks/<songbook_id>/title', methods=['PUT'])
@login_required
def songbook_title(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if current_user.get_id() != songbook.get_owner():
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    data = request.get_json()
    validators.json_request(data)
    data = validators.songbooks_title_request(data)

    songbook.set_title(data['title'])
    g.model.songbooks.save(songbook)

    data['songbook_id'] = songbook_id
    log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

    return jsonify(songbook.get_serialized_data()), 200


@api.route('/songbooks/<songbook_id>/songs', methods=['PUT'])
@login_required
def songbook_songs(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if current_user.get_id() != songbook.get_owner():
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    data = request.get_json()
    validators.json_request(data)
    data = validators.songbooks_songs_request(data)
    data['songs'] = validators.songbook_songs(data['songs'])

    songbook.set_songs(data['songs'])
    g.model.songbooks.save(songbook)

    data['songbook_id'] = songbook_id
    log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

    return jsonify(songbook.get_serialized_data()), 200


@api.route('/songbooks/<songbook_id>/options', methods=['PUT'])
@login_required
def songbook_options(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if current_user.get_id() != songbook.get_owner():
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    data = request.get_json()
    validators.json_request(data)
    data = validators.songbooks_options_request(data)
    data['options'] = validators.songbook_options(data['options'])

    songbook.set_options(data['options'])
    g.model.songbooks.save(songbook)

    data['songbook_id'] = songbook_id
    log_event(EVENTS.SONGBOOK_EDIT, current_user.get_id(), data)

    return jsonify(songbook.get_serialized_data()), 200


app.register_blueprint(api, url_prefix='/api/v1')
