from flask import g
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
from server.util.exceptions import ClientException

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
    return render_template('login.html',
                           login_link=skautis.get_login_url(),
                           app_name=app.config['APP_NAME'])

# Not safe enough
@app.route('/login', methods=['POST']) #FIXME
def login():
    skautis_token = request.form['skautIS_Token']
    skautis_idunit = request.form['skautIS_IDUnit']
    skautis_datelogout = request.form['skautIS_DateLogout']

    user_info = skautis.UserManagement.UserDetail(skautis_token, None)
    user_id = user_info['ID']

    user = g.model.users.find(user_id)
    if user is None:
        user = g.model.users.create_user(user_id, user_info['UserName'], 
                                         user_info['IsActive'], skautis_idunit)

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


api = Blueprint('users', __name__,)


@api.route('/user', methods=['GET'])
@login_required
def get_user_info():
    user = current_user.get_serialized_data()
    user['logout_link'] = skautis.get_logout_url(current_user.get_token())

    return jsonify(user), 200


@api.route('/user/songbook/<songbook_id>', methods=['PUT']) #FIXME
@login_required
def user_songbook(songbook_id):
    songbook = validators.songbook_existence(songbook_id)
    if songbook.get_owner() != current_user and \
       songbook.get_owner_unit() != current_user.get_unit():
        raise ClientException('Tento zpěvník není vlastněn ani tebou ani tvoji jednotkou.', 404)

    current_user.set_active_songbook(songbook_id)
    g.model.users.save(current_user)

    return jsonify({'message': 'Aktivní zpěvník byl změněn.'}), 200


app.register_blueprint(api, url_prefix='/api/v1')
