from flask import g, request, Blueprint

from server.app import app
from server.util import generate_random_filename, generate_tex_file, export_to_pdf
from server.util import validators

import os
import subprocess
import logging
logger = logging.getLogger(__name__)


api = Blueprint('authors', __name__,)

# TODO
@api.route('/authors', methods=['GET', 'POST'])
def songs():
    ip = request.remote_addr
    data = request.get_json()

	return 'Ok', 200

app.register_blueprint(api, url_prefix='/api/v1')


#apix = Blueprint('api2', __name__,)
#
#@apix.route('/test', methods=['POST', 'GET'])
#def songsa():
#    if request.method == 'POST':
#        return "Kulda", 200
#    else:
#        return "Bagr", 200
#
#app.register_blueprint(apix, url_prefix='/api/v1')
