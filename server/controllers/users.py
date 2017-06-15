# -*- coding: UTF-8 -*-

from flask import g
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
from flask import abort

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "users.login"
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
@app.route('/login', methods=['POST'])
def login():
    skautis_token = request.form['skautIS_Token']
    skautis_idunit = request.form['skautIS_IDUnit']
    skautis_datelogout = request.form['skautIS_DateLogout']

    user_info = skautis.UserManagement.UserDetail(skautis_token, None)
    user_id = user_info['ID']

    user = g.model.users.find(user_id)
    if (user is None):
        user = g.model.users.create_user(user_id, user_info['UserName'], user_info['IsActive'], skautis_idunit) #FIXME

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
