#!./__venv__/bin/python3.6

import logging

from server.app import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info('Listening on http://0.0.0.0:%d', app.config['SERVER_PORT'])
    app.run(host='0.0.0.0', port=app.config['SERVER_PORT'])
