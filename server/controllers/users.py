from flask import g
from flask import abort
from flask import render_template
from flask import jsonify
from flask import redirect
from flask import url_for
from flask import request
from flask import Blueprint

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis

from server.util import validators
from server.util import permissions
from server.util.exceptions import ClientException

from server.constants import STRINGS

import zeep

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "index"
login_manager.login_message = u"Přihlaste se pro přístup na tuto stránku"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(userid):
    return g.model.users.find(userid)


@app.route('/')
def index():
    # Render out the login page
    return render_template(
        'login.html', login_link=skautis.get_login_url(), app_name=app.config['APP_NAME'])


@app.route('/login', methods=['POST'])
def login():
    skautis_token = request.form['skautIS_Token']
    skautis_idunit = request.form['skautIS_IDUnit']
    skautis_datelogout = request.form['skautIS_DateLogout']

    try:
        user_info = skautis.UserManagement.UserDetail(skautis_token, None)
    except zeep.exceptions.Fault:
        return redirect(url_for('/'))

    user_id = user_info['ID']
    user = g.model.users.find(user_id)
    if user is None:
        user = g.model.users.create_user(user_id, user_info['UserName'], user_info['IsActive'],
                                         skautis_idunit)

    user.set_token(skautis_token)
    g.model.users.save(user)
    login_user(user)

    arg_next = request.args.get('next')

    return redirect(arg_next or url_for('application'))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    user = current_user
    user.set_token(None)
    g.model.users.save(user)

    logout_user()
    return redirect(url_for('index'))


@app.route('/test_login', methods=['GET'])
def test_login():
    ip = request.remote_addr
    if ip != app.config['SERVER_IP']:
        abort(404)

    user = g.model.users.find(0)
    if user is None:
        user = g.model.users.create_user(0, 'Test', True, 0)

    user.set_token('skautis_token')
    g.model.users.save(user)
    login_user(user)

    return redirect(url_for('test_page'))


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
    if not permissions.check_perm(current_user, songbook, editing=True):
        raise ClientException(STRINGS.PERMISSIONS_NOT_SUFFICIENT, 404)

    current_user.set_active_songbook(songbook_id)
    g.model.users.save(current_user)

    return jsonify({'message': STRINGS.USER_SET_ACTIVE_SONGBOOK}), 200


app.register_blueprint(api, url_prefix='/api/v1')
