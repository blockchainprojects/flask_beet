from uuid import uuid4 as uuid
from flask import (
    session,
    current_app as app
)


def unique_request_id():
    """ Return a unique string
    """
    return str(uuid())


def get_onboarding_account_name():
    return session[app.config.get("BEET_ONBOARDING_ACCOUNT_NAME_KEY")]
