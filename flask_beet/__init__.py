# -*- coding: utf-8 -*-
from pprint import pprint
from flask import current_app, _app_ctx_stack, session
from sqlalchemy import Column, String
from werkzeug.local import LocalProxy
from .utils import unique_request_id
from .views import bp


#: Default configuration
_default_config = {
    "APP_NAME": "Flask-Beet",
    "LOGIN_ENDOINT": "/login/beet",
    "POST_LOGIN_VIEW": "/",
    "ONBOARDING_VIEW": "/register",
    "INVALID_PAYLOAD_MESSAGE": "Invalid payload!",
    "UNIQUE_MESSAGE_GENERATOR": unique_request_id,
    "UNIQUE_MESSAGE_SESSION_KEY": "_signed_message_payload",
    "ONBOARDING_ACCOUNT_NAME_KEY": "_onboarding_account_name",
    "ONBOARDING_MESSAGE_KEY": "_onboarding_message",
    "LOGIN_TEMPLATE": "/beet/login.html",
    "REMEMBER": True,
}


class Beet(object):
    def __init__(self, app=None):
        if app is not None:  # pragma: no cover
            self.init_app(app)

    def init_app(self, app):
        """ Initialize app according to flask factories
        """
        self.app = app
        app.register_blueprint(bp)

        """ Store config variables with BEET_ prefix
        """
        for key, value in _default_config.items():
            app.config.setdefault("BEET_" + key, value)

        @app.context_processor
        def template_extras():
            """ This context processor will throw a random string, store it in
                the session and provide it to the template
            """
            signed_message_payload = app.config.get("BEET_UNIQUE_MESSAGE_GENERATOR")()
            session[
                app.config.get("BEET_UNIQUE_MESSAGE_SESSION_KEY")
            ] = signed_message_payload
            return dict(signed_message_payload=signed_message_payload)

        return app


class BeetMixin:
    """ This mixing is required to have knowledge over which user connects to
        which account
    """

    beet_account_name = Column(String)

    def set_beet_account_name(self, name):
        """ Set a beet account name
        """
        self.beet_account_name = name

    def get_beet_account_name(self):
        """ Get an account name
        """
        return self.beet_account_name

    @classmethod
    def find_beet_account_name(cls, name):
        """ Find a user that has this account name
        """
        return cls.query.filter_by(beet_account_name=name).first()
