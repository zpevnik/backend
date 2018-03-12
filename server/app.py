import os
import time
import logging

from urllib.parse import urlsplit

from flask import Flask
from flask import g
from flask_cors import CORS
from flask_compress import Compress

from colorlog import ColoredFormatter
from pymongo import MongoClient
from skautis import SkautisApi

from server.model import Model

logger = logging.getLogger(__name__)


def setup_handler(handler, level, fmt, use_colors=False):
    handler.setLevel(level)
    if use_colors:
        handler.setFormatter(
            ColoredFormatter(
                "%(log_color)s" + fmt,
                datefmt=None,
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red',
                }))
    else:
        handler.setFormatter(logging.Formatter(fmt))
    return handler


def setup_logging():
    logging.Formatter.converter = time.gmtime

    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)

    consoleFormat = ('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    consoleHandler = setup_handler(
        logging.StreamHandler(), logging.INFO, consoleFormat, use_colors=True)
    rootLogger.addHandler(consoleHandler)


# create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')

# compress the application and handle CORS
Compress(app)
CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

setup_logging()

# initialize SkautIs library
skautis = SkautisApi(app.config['SKAUTIS']['APPID'], test=app.config['SKAUTIS']['TEST'])

# prepare database connection
parsed = urlsplit(app.config['MONGODB_URI'])
mongo_client = MongoClient(app.config['MONGODB_URI'])
db = mongo_client[parsed.path[1:]]

# init model for Zpevnik application
model = Model(db=db)


@app.before_request
def before_request():
    g.model = model


from server import controllers
