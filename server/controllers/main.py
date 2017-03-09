from flask import abort, request, jsonify

from server.app import app
from server.util import AppException

import os
import time

import logging
logger = logging.getLogger(__name__)


@app.errorhandler(AppException)
def handle_AppException(error):
    response = jsonify(error.message)
    response.status_code = error.status_code
    return response

@app.errorhandler(IOError)
def handle_IOError(error):
    response = jsonify(error.filename + ": " + error.strerror)
    response.status_code = 422
    return response

@app.route("/cleanup")
def cleanup():

    ip = request.remote_addr 
    if ip != app.config['SERVER_IP']:
       abort(404)

    logger.info('Cleaning up the temp folder from %s ...' % ip)

    current_time = time.time()

    for f in os.listdir("songs/done"):
        creation_time = os.path.getctime("songs/done/" + f)
        if (current_time - creation_time) > 1800:
            os.unlink("songs/done/" + f)

    return 'Ok'
