import math

from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import current_user
from flask_login import login_required

from server.app import app
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

        # find all results for currect user
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
            response['data'].append(res.get_serialized_data(current_user.get_id()))

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.songs_extended_request(data)
        data['owner'] = current_user.get_id()
        data['visibility'] = data['visibility'] if 'visibility' in data else PERMISSION.PRIVATE

        for author in data['authors']['music']:
            validators.author_existence(author)
        for author in data['authors']['lyrics']:
            validators.author_existence(author)
        for interpreter in data['interpreters']:
            validators.interpreter_existence(interpreter)

        data['variant']['owner'] = current_user.get_id()
        data['variant']['visibility'] = data['variant']['visibility'] if 'visibility' in data[
            'variant'] else PERMISSION.PRIVATE

        validators.song_format(data['variant'])

        song = g.model.songs.create_song(data)
        log_event(EVENTS.SONG_NEW, current_user.get_id(), data)

        data['variant']['song_id'] = song.get_id()

        variant = g.model.variants.create_variant(data['variant'])
        log_event(EVENTS.VARIANT_NEW, current_user.get_id(), data['variant'])

        return jsonify(song.get_serialized_data(current_user.get_id())), 201

        # return jsonify(link='songs/{}/variants/{}'.format(song.get_id(), variant.get_id())), 201, \
        #       {'location': '/songs/{}/variants/{}'.format(song.get_id(), variant.get_id())}


@api.route('/songs/<song_id>', methods=['GET', 'PUT'])
@login_required
def song_single(song_id):
    song = validators.song_existence(song_id)

    if request.method == 'GET':
        return jsonify(song.get_serialized_data(current_user.get_id())), 200

    else:
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

        return jsonify(song.get_serialized_data(current_user.get_id())), 200


@api.route('/songs/<song_id>/variants', methods=['GET', 'POST'])
@login_required
def song_variants(song_id):
    validators.song_existence(song_id)

    if request.method == 'GET':
        result = g.model.variants.find_filtered(current_user.get_id(), song_id=song_id)
        response = []
        for res in result:
            response.append(res.get_serialized_data())

        return jsonify(response), 200

    else:
        data = request.get_json()
        validators.json_request(data)

        data = validators.song_variant_request(data)
        data['song_id'] = song_id
        data['owner'] = current_user.get_id()
        data['visibility'] = data['visibility'] if 'visibility' in data else PERMISSION.PRIVATE

        validators.song_format(data)

        variant = g.model.variants.create_variant(data)
        log_event(EVENTS.VARIANT_NEW, current_user.get_id(), data)

        return jsonify(link='songs/{}/variants/{}'.format(song_id, variant.get_id())), 201, \
              {'location': '/songs/{}/variants/{}'.format(song_id, variant.get_id())}


@api.route('/songs/<song_id>/variants/<variant_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def song_variant_single(song_id, variant_id):
    song = validators.song_existence(song_id)

    variant = validators.song_variant_existence(variant_id)
    if not permissions.check_perm(current_user, variant, visibility=True):
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    if request.method == 'GET':
        return jsonify(variant.get_serialized_data()), 200

    elif request.method == 'PUT':
        if not permissions.check_perm(current_user, variant, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, 403,
                               (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

        data = request.get_json()
        validators.json_request(data)
        data = validators.song_variant_request(data)

        # immediately save test translation into export_cache
        data['export_cache'] = validators.song_format(data)
        variant.set_data(data)

        data['variant_id'] = variant_id
        g.model.variants.save(variant)
        log_event(EVENTS.VARIANT_EDIT, current_user.get_id(), data)

        return jsonify(variant.get_serialized_data()), 200

    else:
        if not permissions.check_perm(current_user, variant, editing=True):
            raise AppException(EVENTS.BASE_EXCEPTION, 403,
                               (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

        g.model.variants.delete(variant)
        log_event(EVENTS.VARIANT_DELETE, current_user.get_id(), variant_id)

        # there is no remaining variant for this song
        if not len(g.model.variants.find(song_id)):
            g.model.songs.delete(song)
            log_event(EVENTS.SONG_DELETE, current_user.get_id(), song_id)

        return jsonify(), 204


@api.route('/songs/<song_id>/variants/<variant_id>/duplicate', methods=['GET'])
@login_required
def song_variant_duplicate(song_id, variant_id):
    validators.song_existence(song_id)

    variant = validators.song_variant_existence(variant_id)
    if not permissions.check_perm(current_user, variant, visibility=True):
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    data = variant.get_serialized_data()
    data['owner'] = current_user.get_id()
    data['visibility'] = PERMISSION.PRIVATE

    g.model.variants.create_variant(data)
    log_event(EVENTS.VARIANT_NEW, current_user.get_id(), data)

    song = validators.song_existence(song_id)

    return jsonify(song.get_serialized_data(current_user.get_id())), 200


app.register_blueprint(api, url_prefix='/api/v1')
