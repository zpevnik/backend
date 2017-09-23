import os
import time

from flask import abort
from flask import request
from flask import jsonify
from flask import make_response
from flask import render_template
from flask import send_from_directory
from flask_login import login_required
from flask_login import current_user

from server.app import app
from server.app import skautis

from server.util import ClientException
from server.util import ValidationException
from server.util import CompilationException
from server.util import TranslationException
from server.util import RequestException
from server.util import log_event

from server.constants import EVENTS


@app.errorhandler(ClientException)
def handle_ClientException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    log_event(EVENTS.CLIENT_EXCEPTION, current_user.get_id(), error.message)
    return response


@app.errorhandler(RequestException)
def handle_RequestException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    log_event(EVENTS.REQUEST_EXCEPTION, current_user.get_id(), error.message)
    return response


@app.errorhandler(CompilationException)
def handle_CompilationException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    log_event(EVENTS.COMPILATION_EXCEPTION, current_user.get_id(), error.message)
    return response


@app.errorhandler(ValidationException)
def handle_ValidationException(error):
    response = jsonify(error.get_json())
    response.status_code = error.status_code
    log_event(EVENTS.VALIDATION_EXCEPTION, current_user.get_id(), error.message)
    return response


@app.errorhandler(TranslationException)
def handle_TranslationException(error):
    response = jsonify(error.get_json())
    response.status_code = error.status_code
    log_event(EVENTS.TRANSLATION_EXCEPTION, current_user.get_id(), error.message)
    return response


@app.errorhandler(IOError)
def handle_IOError(error):
    response = jsonify(error.filename + ": " + error.strerror)
    response.status_code = 500
    log_event(EVENTS.IO_ERROR, current_user.get_id(), error.message)
    return response


@app.route("/test")
@login_required
def test_page():
    user = current_user
    return render_template(
        'test.html', logout_link=skautis.get_logout_url(user.get_token()), username=user.get_name())


@app.route("/application")
@login_required
def application():
    data = current_user.get_serialized_data()
    data['logout_link'] = skautis.get_logout_url(current_user.get_token())

    response = make_response(render_template('app.html', data=data))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/download/<path:filename>', methods=['GET'])
def download(filename):
    directory = os.path.join(os.getcwd(), 'songs/done')
    return send_from_directory(directory=directory, filename=filename)


@app.route("/cleanup")
def cleanup():
    ip = request.remote_addr
    if ip != app.config['SERVER_IP']:
        abort(404)

    log_event(EVENTS.CLEANUP, None, 'Cleaning up the temp folder from {}.'.format(ip))

    current_time = time.time()

    for temp_file in os.listdir("songs/done"):
        creation_time = os.path.getctime("songs/done/" + temp_file)
        if (current_time - creation_time) > 1800:
            os.unlink("songs/done/" + temp_file)

    return 'Ok'
