import os
import time
import logging

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
from server.util import RequestException


logger = logging.getLogger(__name__)


# add logging
@app.errorhandler(ClientException)
def handle_ClientException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    return response

@app.errorhandler(RequestException)
def handle_RequestException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    return response

@app.errorhandler(CompilationException)
def handle_CompilationException(error):
    response = jsonify(message=error.message)
    response.status_code = error.status_code
    return response

@app.errorhandler(ValidationException)
def handle_ValidationException(error):
    response = jsonify(error.get_json())
    response.status_code = error.status_code
    return response

@app.errorhandler(IOError)
def handle_IOError(error):
    response = jsonify(error.filename + ": " + error.strerror)
    response.status_code = 500
    return response

@app.route("/test")
@login_required
def test_page():
    ip = request.remote_addr
    if ip != app.config['SERVER_IP']:
        abort(404)

    user = current_user
    return render_template('test.html', logout_link=skautis.get_logout_url(user.get_token()),
                                        username=user.get_name())

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

    logger.info('Cleaning up the temp folder from %s ...', ip)

    current_time = time.time()

    for temp_file in os.listdir("songs/done"):
        creation_time = os.path.getctime("songs/done/" + temp_file)
        if (current_time - creation_time) > 1800:
            os.unlink("songs/done/" + temp_file)

    return 'Ok'
