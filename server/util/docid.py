import uuid

def generate_random_filename():
    temp = uuid.uuid4().urn
    return temp[9:]

def uuid_to_str(u):
    if u is None:
        return None

    return u.hex

def check_valid_uuid(s):
    try:
        uuid.UUID(hex=s)
    except ValueError:
        return False
    return True

def uuid_from_str(s):
    if s is None:
        return None
    return uuid.UUID(hex=s)

def generate_random_uuid():
    return uuid.uuid4()
