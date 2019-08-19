from uuid import uuid4 as uuid


def unique_request_id():
    """ Return a unique string
    """
    return str(uuid())
