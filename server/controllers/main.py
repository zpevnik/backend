import os
import time

from flask import g
from flask import abort
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for
from flask import make_response
from flask import render_template
from flask import send_from_directory

from flask_login import LoginManager
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis

from server.util import log_event
from server.util import AppException

from server.constants import STRINGS
from server.constants import EVENTS

import zeep

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "index"
login_manager.login_message = u"Přihlaste se pro přístup na tuto stránku"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(userid):
    return g.model.users.find(userid)


@app.errorhandler(AppException)
def handle_AppException(exception):
    # create response from exception data
    response = jsonify(exception.get_exception())
    response.status_code = exception.status_code

    # log exception event and respond
    log_event(exception.exp_type, current_user.get_id(), exception.get_exception())
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    # check whether we have authenticated user
    if not current_user.is_authenticated:
        # render out the login page
        return render_template(
            'login.html', login_link=skautis.get_login_url(), app_name=app.config['APP_NAME'])

    # get base user data
    data = current_user.get_serialized_data()
    data['logout_link'] = skautis.get_logout_url(current_user.get_token())

    # set some response headers
    response = make_response(render_template('app.html', data=data))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    # return and render out the application (frontend router will handle path)
    return response


@app.route('/login', methods=['POST'])
def login():
    # get skautIS credentials from POST request
    skautis_token = request.form['skautIS_Token']
    skautis_idunit = request.form['skautIS_IDUnit']
    skautis_datelogout = request.form['skautIS_DateLogout']

    # get additional data about user from the skautIS
    try:
        user_info = skautis.UserManagement.UserDetail(skautis_token, None)
    except zeep.exceptions.Fault:
        # something weird happened and skautIS data were not received
        return redirect(url_for('/'))

    # find user in our database
    user = g.model.users.find(user_info['ID'])
    if user is None:
        # create new user if this is first visit here
        user = g.model.users.create_user(user_info['ID'], user_info['UserName'],
                                         user_info['IsActive'], skautis_idunit)

    # save user token for possible future usage
    user.set_token(skautis_token)
    g.model.users.save(user)

    login_user(user)

    # redirect logged in user according to next arg
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    user = current_user

    # reset skautIS token so that it cannot be used anymore
    user.set_token(None)
    g.model.users.save(user)

    # logout user and redirect
    logout_user()
    return redirect(url_for('index'))


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    # send rendered out pdf with nices name
    directory = os.path.join(os.getcwd(), app.config['SONGBOOK_DONE_FOLDER'])
    return send_from_directory(
        directory=directory,
        filename=filename)
#        as_attachment=True,
#        attachment_filename="Zpevnik.pdf")


@app.route("/cleanup")  # NOT TESTED! TODO
def cleanup():
    ip = request.remote_addr
    if ip != app.config['SERVER_IP']:
        abort(404)

    log_event(EVENTS.CLEANUP, None, 'Cleaning up the temp folder from {}.'.format(ip))

    # go through every songbook and check its cache
    valid_files = []
    songbooks = g.model.songbooks.find()
    for songbook in songbooks:
        # check whether this songbook is cached
        if songbook.is_cached():
            if not songbook.is_cache_valid():
                # invalidate cache in case that time is up
                songbook.invalidate_cache()
                g.model.songbooks.save(songbook)
            else:
                # append cached file as valid
                valid_files.append(get_cached_file() + '.pdf')

    # check every file in done folder and delete invalid ones
    for temp_file in os.listdir(app.config['SONGBOOK_DONE_FOLDER']):
        if temp_file not in valid_files:
            os.unlink(app.config['SONGBOOK_DONE_FOLDER'] + temp_file)

    return 'Ok'


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


@app.route("/test")
@login_required
def test_page():
    user = current_user
    return render_template(
        'test.html', logout_link=skautis.get_logout_url(user.get_token()), username=user.get_name())
