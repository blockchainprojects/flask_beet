from uuid import uuid4 as uuid


def unique_request_id():
    return str(uuid())
