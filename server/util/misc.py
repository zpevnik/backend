import uuid
import logging


def generate_random_filename():
    temp = uuid.uuid4().urn
    return temp[9:]


def log_event(event, user, data):
    logger = logging.getLogger(__name__)
    logger.info('[{}] user: {}, data: {}'.format(event, user, data))


def merge_lists(l1, l2, key):
    merged = {}
    for item in l1 + l2:
        if item[key] in merged:
            merged[item[key]].update(item)
        else:
            merged[item[key]] = item
    return [val for (_, val) in merged.items()]
