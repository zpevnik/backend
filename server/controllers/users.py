from flask import g
from flask import jsonify
from flask import request
from flask import Blueprint
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis
from server.util import validators
from server.util import permissions
from server.util import log_event
from server.util.exceptions import AppException

from server.constants import EVENTS
from server.constants import EXCODES
from server.constants import STRINGS

import zeep

api = Blueprint('users', __name__)


@api.route('/user', methods=['GET'])
@login_required
def get_user_info():
    user = current_user.get_serialized_data()
    user['logout_link'] = skautis.get_logout_url(current_user.get_token())

    return jsonify(user), 200


@api.route('/users/<user_id>', methods=['GET'])
@login_required
def get_other_user_info(user_id):
    user = validators.user_existence(user_id)
    return jsonify({'name': user.get_name()}), 200


@api.route('/users/songbook/<songbook_id>', methods=['PUT'])
@login_required
def user_songbook(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if current_user.get_id() != songbook.get_owner():
        raise AppException(EVENTS.BASE_EXCEPTION, 403,
                           (EXCODES.INSUFFICIENT_PERMISSIONS, STRINGS.INSUFFICIENT_PERMISSIONS))

    current_user.set_active_songbook(songbook_id)
    g.model.users.save(current_user)

    return jsonify({'message': STRINGS.USER_SET_ACTIVE_SONGBOOK}), 200


app.register_blueprint(api, url_prefix='/api/v1')
