from flask import Flask, g
from flask_compress import Compress

from pymongo import MongoClient
from server.skautis import Skautis
from server.model import Model

import time
from logging import StreamHandler, Formatter
from colorlog import ColoredFormatter

import logging
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
        handler.setFormatter(Formatter(fmt))
    return handler

def setup_logging():
    logging.Formatter.converter = time.gmtime

    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.DEBUG)

    consoleFormat = ('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    consoleHandler = setup_handler(StreamHandler(), logging.DEBUG, consoleFormat, use_colors=True)
    rootLogger.addHandler(consoleHandler)


app = Flask(__name__)
app.config.from_pyfile('config.py')

Compress(app)

setup_logging()

#skautis = Skautis(app.config['SKAUTIS']['SECRET'])

mongoClient = MongoClient(app.config['MONGODB']['URL'])
db = mongoClient[app.config['MONGODB']['DB']]

model = Model(db=db)

@app.before_request
def before_request():
    g.model = model

from server import controllers
