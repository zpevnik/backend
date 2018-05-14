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

api = Blueprint('variants', __name__)


@api.route('/variants', methods=['GET'])
@login_required
def variants():
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

    songs = []

    for res in result:
        songs.append(res.get_serialized_data(current_user.get_id()))

    # remove nesting - explode variants into response and add song data
    for song in songs:
        for variant in song['variants']:
            variant['song'] = {
                'id': song['id'],
                'created': song['created'],
                'title': song['title'],
                'authors': song['authors'],
                'interpreters': song['interpreters']
            }
            response['data'].append(variant)

    return jsonify(response), 200


app.register_blueprint(api, url_prefix='/api/v1')
