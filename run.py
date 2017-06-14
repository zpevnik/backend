#!/usr/bin/env python

import logging
import gevent.monkey

from server.app import app
from socketio.server import SocketIOServer
from werkzeug.serving import run_with_reloader

gevent.monkey.patch_all()

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Listening on http://0.0.0.0:%d', app.config['SERVER_PORT'])

    server = SocketIOServer(('0.0.0.0', app.config['SERVER_PORT']), app, resource="socket.io")

    if app.config['DEVELOPMENT']:
        def run_server():
            server.serve_forever()
        run_with_reloader(run_server)
    else:
        server.serve_forever()
