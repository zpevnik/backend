import uuid
import logging


def generate_random_filename():
    temp = uuid.uuid4().urn
    return temp[9:]


def log_event(event, user, data):
    logger = logging.getLogger(__name__)
    logger.info('[{}] user: {}, data: {}'.format(event, user, data))
