from flask import g
from flask import jsonify
from flask import Blueprint
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis
from server.util import validators

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


app.register_blueprint(api, url_prefix='/api/v1')
