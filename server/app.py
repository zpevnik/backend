import time
import logging

from flask import Flask
from flask import g
from flask_compress import Compress
from urlparse import urlsplit
from pymongo import MongoClient
from colorlog import ColoredFormatter
from skautis import SkautisApi

from server.model import Model

logger = logging.getLogger(__name__)


def setup_handler(handler, level, fmt, use_colors=False):
    handler.setLevel(level)
    if use_colors:
        handler.setFormatter(ColoredFormatter(
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
    rootLogger.setLevel(logging.DEBUG)

    consoleFormat = ('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    consoleHandler = setup_handler(logging.StreamHandler(), logging.DEBUG,
                                   consoleFormat, use_colors=True)
    rootLogger.addHandler(consoleHandler)


app = Flask(__name__)
app.config.from_pyfile('config.py')

Compress(app)
setup_logging()

parsed = urlsplit(app.config['MONGODB_URI'])

skautis = SkautisApi(app.config['SKAUTIS']['APPID'],test=app.config['SKAUTIS']['TEST'])
mongoClient = MongoClient(app.config['MONGODB_URI'])
db = mongoClient[parsed.path[1:]]

# Authenticate
if '@' in app.config['MONGODB_URI']:
    user, password = parsed.netloc.split('@')[0].split(':')
    db.authenticate(user, password)

model = Model(db=db)

@app.before_request
def before_request():
    g.model = model

from server import controllers
